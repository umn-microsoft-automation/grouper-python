from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .group import Group
    from .client import Client

from pydantic import BaseModel
from enum import StrEnum, auto
from .subject import Subject

from .exceptions import GrouperGroupNotFoundException, GrouperSuccessException


class MembershipType(StrEnum):
    DIRECT = auto()
    INDIRECT = auto()


class MemberType(StrEnum):
    USER = auto()
    GROUP = auto()


class Membership(BaseModel):
    member: Subject
    member_type: MemberType
    membership_type: MembershipType


def get_memberships_for_groups(
    group_names: list[str],
    client: Client,
    attributes: list[str] = [],
    member_filter: str = "all",
    resolve_groups: bool = True,
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> dict[Group, list[Membership]]:
    from .group import Group
    from .user import User

    if resolve_groups:
        from .util import get_group_by_name

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
