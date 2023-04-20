from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .objects.group import Group
    from .objects.client import Client
    from .objects.membership import Membership, HasMember
    from .objects.subject import Subject

# from pydantic import BaseModel
# from enum import StrEnum, auto
# from .subject import Subject

from .objects.exceptions import (
    GrouperGroupNotFoundException,
    GrouperSuccessException,
    GrouperPermissionDenied,
)
# from .objects.membership import Membership, MembershipType, MemberType, HasMember

from .group import get_group_by_name


# class MembershipType(StrEnum):
#     DIRECT = auto()
#     INDIRECT = auto()


# class MemberType(StrEnum):
#     USER = auto()
#     GROUP = auto()


# class Membership(BaseModel):
#     member: Subject
#     member_type: MemberType
#     membership_type: MembershipType


def get_memberships_for_groups(
    group_names: list[str],
    client: Client,
    attributes: list[str] = [],
    member_filter: str = "all",
    resolve_groups: bool = True,
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> dict[Group, list[Membership]]:
    from .objects.membership import Membership, MembershipType, MemberType
    from .objects.group import Group
    from .objects.user import User
    from .objects.subject import Subject

    attribute_set = set(attributes + [client.universal_id_attr, "name"])

    group_lookup = [{"groupName": group} for group in group_names]
    body = {
        "WsRestGetMembershipsRequest": {
            "subjectAttributeNames": [*attribute_set],
            "includeSubjectDetail": "T",
            "includeGroupDetail": "T",
            "memberFilter": member_filter,
            "wsGroupLookups": group_lookup,
        }
    }
    try:
        r = client._call_grouper(
            "/memberships",
            body,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
        # r = call_grouper(
        #     client,
        #     "/memberships",
        #     body,
        #     act_as_subject_id=act_as_subject_id,
        #     act_as_subject_identifier=act_as_subject_identifier,
        # )
    except GrouperSuccessException as err:
        r = err.grouper_result
        meta = r["WsGetMembershipsResults"]["resultMetadata"]
        if meta["resultCode"] == "GROUP_NOT_FOUND":
            try:
                result_message = meta["resultMessage"]
                split_message = result_message.split(",")
                group_name = split_message[2].split("=")[1]
            except Exception:
                raise
            raise GrouperGroupNotFoundException(group_name)
        else:  # pragma: no cover
            raise
    if "wsGroups" not in r["WsGetMembershipsResults"].keys():
        # if "wsGroups" is not in the result but it was succesful,
        # that means the group(s) exist but have no memberships
        # This function will only return groups with memberships,
        # so this means there are no memberships and we return
        # an empty dict
        return {}
    ws_memberships = r["WsGetMembershipsResults"].get("wsMemberships", [])
    ws_groups = r["WsGetMembershipsResults"]["wsGroups"]
    ws_subjects = r["WsGetMembershipsResults"].get("wsSubjects", [])
    subjects = {ws_subject["id"]: ws_subject for ws_subject in ws_subjects}
    groups = {
        ws_group["uuid"]: Group.from_results(client, ws_group) for ws_group in ws_groups
    }
    r_attributes = r["WsGetMembershipsResults"].get("subjectAttributeNames", [])
    r_dict: dict[Group, list[Membership]] = {group: [] for group in groups.values()}
    for ws_membership in ws_memberships:
        subject: Subject
        if ws_membership["subjectSourceId"] == "g:gsa":
            member_type = MemberType.GROUP
            if resolve_groups:
                subject = get_group_by_name(
                    subjects[ws_membership["subjectId"]]["name"], client
                )
            else:
                subject = Subject.from_results(
                    client, subjects[ws_membership["subjectId"]], r_attributes, "name"
                )
        else:
            member_type = MemberType.USER
            subject = User.from_results(
                client,
                subjects[ws_membership["subjectId"]],
                r_attributes,
                client.universal_id_attr,
            )

        if ws_membership["membershipType"] == "immediate":
            membership_type = MembershipType.DIRECT
        elif ws_membership["membershipType"] == "effective":
            membership_type = MembershipType.INDIRECT
        else:
            raise GrouperSuccessException(r)

        membership = Membership(
            member=subject, member_type=member_type, membership_type=membership_type
        )
        group = groups[ws_membership["groupId"]]
        r_dict[group].append(membership)
    return r_dict


def has_members(
    group_name: str,
    client: Client,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
    member_filter: str = "all",
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> dict[str, HasMember]:
    from .objects.membership import HasMember

    if (subject_identifiers and subject_ids) or (
        not subject_identifiers and not subject_ids
    ):
        raise ValueError(
            "Exactly one of subject_identifiers or subject_ids must be specified"
        )
    subject_lookups = []
    if subject_identifiers:
        subject_lookups = [
            {"subjectIdentifier": ident} for ident in subject_identifiers
        ]
        ident_key = "identifierLookup"
    elif subject_ids:
        subject_lookups = [{"subjectId": ident} for ident in subject_ids]
        ident_key = "id"
    body = {
        "WsRestHasMemberRequest": {
            "subjectLookups": subject_lookups,
            "memberFilter": member_filter,
        }
    }
    try:
        r = client._call_grouper(
            f"/groups/{group_name}/members",
            body,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        if r["WsHasMemberResults"]["resultMetadata"]["resultCode"] == "GROUP_NOT_FOUND":
            raise GrouperGroupNotFoundException(group_name)
        else:  # pragma: no cover
            raise
    results = r["WsHasMemberResults"]["results"]
    r_dict = {}
    for result in results:
        meta_keys = result["resultMetadata"].keys()
        if "resultCode2" in meta_keys:
            if result["resultMetadata"]["resultCode2"] == "SUBJECT_NOT_FOUND":
                is_member = HasMember.SUBJECT_NOT_FOUND
                ident = result["wsSubject"]["id"]
            else:
                raise GrouperSuccessException(r)
        if result["resultMetadata"]["resultCode"] == "IS_NOT_MEMBER":
            is_member = HasMember.IS_NOT_MEMBER
            ident = result["wsSubject"][ident_key]
        elif result["resultMetadata"]["resultCode"] == "IS_MEMBER":
            is_member = HasMember.IS_MEMBER
            ident = result["wsSubject"][ident_key]
        else:
            raise GrouperSuccessException(r)
        r_dict[ident] = is_member
    return r_dict


def add_members_to_group(
    group_name: str,
    client: Client,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
    replace_all_existing: str = "F",
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> Group:
    from .objects.group import Group

    identifiers_to_add = [{"subjectIdentifier": ident} for ident in subject_identifiers]
    ids_to_add = [{"subjectId": sid} for sid in subject_ids]
    subjects_to_add = identifiers_to_add + ids_to_add
    body = {
        "WsRestAddMemberRequest": {
            "subjectLookups": subjects_to_add,
            "wsGroupLookup": {"groupName": group_name},
            "replaceAllExisting": replace_all_existing,
            "includeGroupDetail": "T",
        }
    }
    try:
        r = client._call_grouper(
            "/groups",
            body,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        if r["WsAddMemberResults"]["resultMetadata"]["resultCode"] == "GROUP_NOT_FOUND":
            raise GrouperGroupNotFoundException(group_name)
        elif (
            r["WsAddMemberResults"]["resultMetadata"]["resultCode"]
            == "PROBLEM_WITH_ASSIGNMENT"
            and r["WsAddMemberResults"]["results"][0]["resultMetadata"]["resultCode"]
            == "INSUFFICIENT_PRIVILEGES"
        ):
            raise GrouperPermissionDenied()
        else:  # pragma: no cover
            raise
    return Group.from_results(client, r["WsAddMemberResults"]["wsGroupAssigned"])


def delete_members_from_group(
    group_name: str,
    client: Client,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> Group:
    from .objects.group import Group

    identifiers_to_delete = [
        {"subjectIdentifier": ident} for ident in subject_identifiers
    ]
    ids_to_delete = [{"subjectId": sid} for sid in subject_ids]
    subjects_to_delete = identifiers_to_delete + ids_to_delete
    body = {
        "WsRestDeleteMemberRequest": {
            "subjectLookups": subjects_to_delete,
            "wsGroupLookup": {"groupName": group_name},
            "includeGroupDetail": "T",
        }
    }
    print(body)
    try:
        r = client._call_grouper(
            "/groups",
            body,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        if (
            r["WsDeleteMemberResults"]["resultMetadata"]["resultCode"]
            == "GROUP_NOT_FOUND"
        ):
            raise GrouperGroupNotFoundException(group_name)
        elif (
            r["WsDeleteMemberResults"]["resultMetadata"]["resultCode"]
            == "PROBLEM_DELETING_MEMBERS"
            and r["WsDeleteMemberResults"]["results"][0]["resultMetadata"]["resultCode"]
            == "INSUFFICIENT_PRIVILEGES"
        ):
            raise GrouperPermissionDenied()
        else:  # pragma: no cover
            raise
    return Group.from_results(client, r["WsDeleteMemberResults"]["wsGroup"])


def get_members_for_groups(
    group_names: list[str],
    client: Client,
    attributes: list[str] = [],
    member_filter: str = "all",
    resolve_groups: bool = True,
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> dict[Group, list[Subject]]:
    from .objects.user import User
    from .objects.group import Group
    from .objects.subject import Subject

    group_lookup = [{"groupName": group} for group in group_names]
    body = {
        "WsRestGetMembersRequest": {
            "subjectAttributeNames": attributes,
            "wsGroupLookups": group_lookup,
            "memberFilter": member_filter,
            "includeSubjectDetail": "T",
        }
    }
    r = client._call_grouper(
        "/groups",
        body,
        act_as_subject_id=act_as_subject_id,
        act_as_subject_identifier=act_as_subject_identifier,
    )
    r_dict: dict[Group, list[Subject]] = {}
    r_attributes = r["WsGetMembersResults"]["subjectAttributeNames"]
    for result in r["WsGetMembersResults"]["results"]:
        members: list[Subject] = []
        key = Group.from_results(client, result["wsGroup"])
        if result["resultMetadata"]["success"] == "T":
            if "wsSubjects" in result:
                for subject in result["wsSubjects"]:
                    if subject["sourceId"] == "g:gsa":
                        if resolve_groups:
                            group = get_group_by_name(subject["name"], client)
                            members.append(group)
                        else:
                            # subject = Subject(
                            #     id=subject["id"],
                            #     description=subject["attributeValues"][
                            #         description_index
                            #     ],
                            #     universal_id=subject["name"],
                            #     client=client,
                            # )
                            subject = Subject.from_results(
                                client=client,
                                subject_body=subject,
                                subject_attr_names=r_attributes,
                            )
                            members.append(subject)
                    else:
                        user = User.from_results(
                            client=client,
                            user_body=subject,
                            subject_attr_names=r_attributes,
                        )
                        members.append(user)
            else:
                pass
            r_dict[key] = members
        else:
            pass
    return r_dict
