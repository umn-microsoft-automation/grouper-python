"""grouper-python.membership - functions to interact with grouper membership.

These are "helper" functions that most likely will not be called directly.
Instead, a GrouperClient class should be created, then from there use that
GrouperClient's methods to find and create objects, and use those objects' methods.
These helper functions are used by those objects, but can be called
directly if needed.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .objects.group import Group
    from .objects.client import GrouperClient
    from .objects.membership import Membership, HasMember
    from .objects.subject import Subject
from .objects.exceptions import (
    GrouperGroupNotFoundException,
    GrouperSuccessException,
    GrouperPermissionDenied,
)
from .util import resolve_subject


def get_memberships_for_groups(
    group_names: list[str],
    client: GrouperClient,
    attributes: list[str] = [],
    member_filter: str = "all",
    resolve_groups: bool = True,
    act_as_subject: Subject | None = None,
) -> dict[Group, list[Membership]]:
    """Get memberships for the given groups.

    Note that a "membership" includes more detail than a "member".

    :param group_names: Group names to retreive memberships for
    :type group_names: list[str]
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param attributes: Additional attributes to retrieve for the Subjects,
    defaults to []
    :type attributes: list[str], optional
    :param member_filter: Type of mebership to return (all, immediate, effective),
    defaults to "all"
    :type member_filter: str, optional
    :param resolve_groups: Whether to resolve subjects that are groups into Group
    objects, which will require an additional API call per group, defaults to True
    :type resolve_groups: bool, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises GrouperGroupNotFoundException: A group with the given name cannot
    be found
    :raises GrouperSuccessException: An otherwise unhandled issue with the result
    :return: A dictionary with Groups as the keys
    and those groups' memberships list as the value
    :rtype: dict[Group, list[Membership]]
    """
    from .objects.membership import Membership, MembershipType, MemberType
    from .objects.group import Group

    attribute_set = set(attributes + [client.universal_identifier_attr, "name"])

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
            act_as_subject=act_as_subject,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        meta = r["WsGetMembershipsResults"]["resultMetadata"]
        if meta["resultCode"] == "GROUP_NOT_FOUND":
            try:
                result_message = meta["resultMessage"]
                split_message = result_message.split(",")
                group_name = split_message[2].split("=")[1]
            except Exception:  # pragma: no cover
                # The try above feels fragile, so if it fails,
                # throw the original SuccessException
                raise err
            raise GrouperGroupNotFoundException(group_name, r)
        else:  # pragma: no cover
            # We don't know what exactly has happened here
            raise err
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
        ws_group["uuid"]: Group(client, ws_group) for ws_group in ws_groups
    }
    subject_attr_names = r["WsGetMembershipsResults"].get("subjectAttributeNames", [])
    r_dict: dict[Group, list[Membership]] = {group: [] for group in groups.values()}
    for ws_membership in ws_memberships:
        subject = resolve_subject(
            subject_body=subjects[ws_membership["subjectId"]],
            client=client,
            subject_attr_names=subject_attr_names,
            resolve_group=resolve_groups,
        )
        if ws_membership["subjectSourceId"] == "g:gsa":
            member_type = MemberType.GROUP
        else:
            member_type = MemberType.PERSON

        if ws_membership["membershipType"] == "immediate":
            membership_type = MembershipType.DIRECT
        elif ws_membership["membershipType"] == "effective":
            membership_type = MembershipType.INDIRECT
        else:  # pragma: no cover
            # Unknown membershipType, we don't know what's going on,
            # so raise a SuccessException
            raise GrouperSuccessException(r)

        membership = Membership(
            member=subject, member_type=member_type, membership_type=membership_type
        )
        group = groups[ws_membership["groupId"]]
        r_dict[group].append(membership)
    return r_dict


def has_members(
    group_name: str,
    client: GrouperClient,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
    member_filter: str = "all",
    act_as_subject: Subject | None = None,
) -> dict[str, HasMember]:
    """Determine if the given subjects are members of the given group.

    :param group_name: Name of group to check members
    :type group_name: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param subject_identifiers: Subject identifiers to check for membership,
    defaults to []
    :type subject_identifiers: list[str], optional
    :param subject_ids: Subject ids to check for membership,
    defaults to [], defaults to []
    :type subject_ids: list[str], optional
    :param member_filter: Type of mebership to return (all, immediate, effective),
    defaults to "all"
    :type member_filter: str, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises ValueError: No subjects were specified
    :raises GrouperGroupNotFoundException: A group with the given name cannot
    be found
    :raises GrouperSuccessException: An otherwise unhandled issue with the result
    :return: A dict with the key being the subject (either identifier or id)
    and the value being a HasMember enum.
    :rtype: dict[str, HasMember]
    """
    from .objects.membership import HasMember

    if not subject_identifiers and not subject_ids:
        raise ValueError(
            "At least one of subject_identifiers or subject_ids must be specified"
        )
    subject_identifier_lookups = [
        {"subjectIdentifier": ident} for ident in subject_identifiers
    ]
    subject_id_lookups = [{"subjectId": ident} for ident in subject_ids]
    body = {
        "WsRestHasMemberRequest": {
            "subjectLookups": subject_identifier_lookups + subject_id_lookups,
            "memberFilter": member_filter,
        }
    }
    try:
        r = client._call_grouper(
            f"/groups/{group_name}/members",
            body,
            act_as_subject=act_as_subject,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        if r["WsHasMemberResults"]["resultMetadata"]["resultCode"] == "GROUP_NOT_FOUND":
            raise GrouperGroupNotFoundException(group_name, r)
        else:  # pragma: no cover
            # We're not sure what exactly has happened here,
            # So raise the original SuccessException
            raise err
    results = r["WsHasMemberResults"]["results"]
    r_dict = {}
    for result in results:
        meta_keys = result["resultMetadata"].keys()
        if "resultCode2" in meta_keys:
            if result["resultMetadata"]["resultCode2"] == "SUBJECT_NOT_FOUND":
                is_member = HasMember.SUBJECT_NOT_FOUND
                ident = result["wsSubject"]["id"]
            else:  # pragma: no cover
                # We're not sure what exactly has happened here,
                # So raise a SuccessException
                raise GrouperSuccessException(r)
        else:
            if "identifierLookup" in result["wsSubject"]:
                ident_key = "identifierLookup"
            elif "id" in result["wsSubject"]:
                ident_key = "id"
            else:  # pragma: no cover
                # We're not sure what exactly has happened here,
                # So raise a SuccessException
                raise GrouperSuccessException(r)
            if result["resultMetadata"]["resultCode"] == "IS_NOT_MEMBER":
                is_member = HasMember.IS_NOT_MEMBER
                ident = result["wsSubject"][ident_key]
            elif result["resultMetadata"]["resultCode"] == "IS_MEMBER":
                is_member = HasMember.IS_MEMBER
                ident = result["wsSubject"][ident_key]
            else:  # pragma: no cover
                # We're not sure what exactly has happened here,
                # So raise a SuccessException
                raise GrouperSuccessException(r)
        r_dict[ident] = is_member
    return r_dict


def add_members_to_group(
    group_name: str,
    client: GrouperClient,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
    replace_all_existing: str = "F",
    act_as_subject: Subject | None = None,
) -> Group:
    """Add members to a group.

    :param group_name: The group to add members to
    :type group_name: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param subject_identifiers: Subject identifiers of members to add, defaults to []
    :type subject_identifiers: list[str], optional
    :param subject_ids: Subject ids of members to add, defaults to []
    :type subject_ids: list[str], optional
    :param replace_all_existing: Whether to replace existing membership of group,
    "T" will replace, "F" will only add members, defaults to "F"
    :type replace_all_existing: str, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises GrouperGroupNotFoundException: A group with the given name cannot
    be found
    :raises GrouperPermissionDenied: Permission denied to complete the operation
    :raises GrouperSuccessException: An otherwise unhandled issue with the result
    :return: A Group object representing the group that members were added to
    :rtype: Group
    """
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
            act_as_subject=act_as_subject,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        if r["WsAddMemberResults"]["resultMetadata"]["resultCode"] == "GROUP_NOT_FOUND":
            raise GrouperGroupNotFoundException(group_name, r)
        elif (
            r["WsAddMemberResults"]["resultMetadata"]["resultCode"]
            == "PROBLEM_WITH_ASSIGNMENT"
            and r["WsAddMemberResults"]["results"][0]["resultMetadata"]["resultCode"]
            == "INSUFFICIENT_PRIVILEGES"
        ):
            raise GrouperPermissionDenied(r)
        else:  # pragma: no cover
            # We're not sure what exactly has happened here,
            # So raise the original SuccessException
            raise err
    return Group(client, r["WsAddMemberResults"]["wsGroupAssigned"])


def delete_members_from_group(
    group_name: str,
    client: GrouperClient,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
    act_as_subject: Subject | None = None,
) -> Group:
    """Remove members from a group.

    :param group_name: The name of the group to remove members from
    :type group_name: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param subject_identifiers: Subject identifiers of members to remove, defaults to []
    :type subject_identifiers: list[str], optional
    :param subject_ids: Subject ids of members to remove, defaults to []
    :type subject_ids: list[str], optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises GrouperGroupNotFoundException: A group with the given name cannot
    be found
    :raises GrouperPermissionDenied: Permission denied to complete the operation
    :raises GrouperSuccessException: An otherwise unhandled issue with the result
    :return: A Group object representing the group that members were removed from
    :rtype: Group
    """
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
    try:
        r = client._call_grouper(
            "/groups",
            body,
            act_as_subject=act_as_subject,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        if (
            r["WsDeleteMemberResults"]["resultMetadata"]["resultCode"]
            == "GROUP_NOT_FOUND"
        ):
            raise GrouperGroupNotFoundException(group_name, r)
        elif (
            r["WsDeleteMemberResults"]["resultMetadata"]["resultCode"]
            == "PROBLEM_DELETING_MEMBERS"
            and r["WsDeleteMemberResults"]["results"][0]["resultMetadata"]["resultCode"]
            == "INSUFFICIENT_PRIVILEGES"
        ):
            raise GrouperPermissionDenied(r)
        else:  # pragma: no cover
            # We're not sure what exactly has happened here,
            # So raise the original SuccessException
            raise err
    return Group(client, r["WsDeleteMemberResults"]["wsGroup"])


def get_members_for_groups(
    group_names: list[str],
    client: GrouperClient,
    attributes: list[str] = [],
    member_filter: str = "all",
    resolve_groups: bool = True,
    act_as_subject: Subject | None = None,
) -> dict[Group, list[Subject]]:
    """Get members for the given groups.

    :param group_names: Group names to retreive members for
    :type group_names: list[str]
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param attributes: Additional attributes to retrieve for the Subjects,
    defaults to []
    :type attributes: list[str], optional
    :param member_filter: Type of mebership to return (all, immediate, effective),
    defaults to "all"
    :type member_filter: str, optional
    :param resolve_groups: Whether to resolve subjects that are groups into Group
    objects, which will require an additional API call per group, defaults to True
    :type resolve_groups: bool, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises GrouperGroupNotFoundException: A group with the given name cannot
    be found
    :raises GrouperSuccessException: An otherwise unhandled issue with the result
    :return: A dictionary with Groups as the keys
    and those groups' member list as the value
    :rtype: dict[Group, list[Subject]]
    """
    from .objects.group import Group

    group_lookup = [{"groupName": group} for group in group_names]
    body = {
        "WsRestGetMembersRequest": {
            "subjectAttributeNames": attributes,
            "wsGroupLookups": group_lookup,
            "memberFilter": member_filter,
            "includeSubjectDetail": "T",
        }
    }
    try:
        r = client._call_grouper(
            "/groups",
            body,
            act_as_subject=act_as_subject,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        for result in r["WsGetMembersResults"]["results"]:
            meta = result["resultMetadata"]
            if meta["success"] == "F":
                if meta["resultCode"] == "GROUP_NOT_FOUND":
                    try:
                        result_message = meta["resultMessage"]
                        split_message = result_message.split(",")
                        group_name = split_message[2].split("=")[1]
                    except Exception:  # pragma: no cover
                        # The try above feels fragile, so if it fails,
                        # throw the original SuccessException
                        raise err
                    raise GrouperGroupNotFoundException(group_name, r)
                else:  # pragma: no cover
                    # We're not sure what exactly has happened here,
                    # So raise the original SuccessException
                    raise err
            else:
                pass
        # If we've gotten here, we don't know what's going on,
        # So raise the original SuccessException
        raise err  # pragma: no cover
    r_dict: dict[Group, list[Subject]] = {}
    subject_attr_names = r["WsGetMembersResults"]["subjectAttributeNames"]
    for result in r["WsGetMembersResults"]["results"]:
        # members: list[Subject] = []
        key = Group(client, result["wsGroup"])
        if result["resultMetadata"]["success"] == "T":
            if "wsSubjects" in result:
                members = [
                    resolve_subject(
                        subject_body=subject,
                        client=client,
                        subject_attr_names=subject_attr_names,
                        resolve_group=resolve_groups,
                    )
                    for subject in result["wsSubjects"]
                ]
            else:
                members = []
            r_dict[key] = members
        else:  # pragma: no cover
            # we don't know what's going on,
            # so raise a SuccessException
            raise GrouperSuccessException(r)
    return r_dict
