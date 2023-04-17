from typing import Any

# if TYPE_CHECKING:
#     from .subject import Subject

import httpx
from enum import Enum

# from pydantic import BaseModel
from .util import call_grouper
from .subject import Subject
from .privilege import assign_privilege
from .exceptions import (
    GrouperGroupNotFoundException,
    GrouperSuccessException,
    GrouperStemNotFoundException,
    GrouperPermissionDenied,
)


class Group(Subject):
    extension: str
    displayName: str
    uuid: str
    enabled: str
    displayExtension: str
    name: str
    typeOfGroup: str
    idIndex: str
    detail: dict[str, Any] | None

    @classmethod
    def from_results(
        cls: type["Group"], client: httpx.Client, group_body: dict[str, Any]
    ) -> "Group":
        return cls(
            id=group_body["uuid"],
            description=group_body.get("description", ""),
            universal_id=group_body["name"],
            extension=group_body["extension"],
            displayName=group_body["displayName"],
            uuid=group_body["uuid"],
            enabled=group_body["enabled"],
            displayExtension=group_body["displayExtension"],
            name=group_body["name"],
            typeOfGroup=group_body["typeOfGroup"],
            idIndex=group_body["idIndex"],
            detail=group_body.get("detail"),
            client=client,
        )

    # def __init__(self, client: httpx.Client, group_body: dict[str, Any]) -> None:
    # super().__init__(
    #     extension=group_body["extension"],
    #     displayName=group_body["displayName"],
    #     description=group_body.get("description", ""),
    #     uuid=group_body["uuid"],
    #     id=group_body["uuid"],
    #     enabled=group_body["enabled"],
    #     displayExtension=group_body["displayExtension"],
    #     name=group_body["name"],
    #     typeOfGroup=group_body["typeOfGroup"],
    #     idIndex=group_body["idIndex"],
    #     detail=group_body.get("detail"),
    #     client=client,
    # )
    #     self.client = client
    #     self.extension = group_body["extension"]
    #     self.displayName = group_body["displayName"]
    #     self.description = group_body.get("description", "")
    #     self.uuid = group_body["uuid"]
    #     self.id = self.uuid
    #     self.enabled = group_body["enabled"]
    #     self.displayExtension = group_body["displayExtension"]
    #     self.name = group_body["name"]
    #     self.typeOfGroup = group_body["typeOfGroup"]
    #     self.idIndex = group_body["idIndex"]
    #     self.detail: dict[str, Any] | None = group_body.get("detail")

    # def __repr__(self) -> str:
    #     return f"<Grouper Group {self.name}>"
    # class Config:
    #     arbitrary_types_allowed = True

    def get_members(
        self,
        attributes: list[str] = [],
        member_filter: str = "all",
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> list["Subject"]:
        members = get_members_for_groups(
            groups=[self],
            client=self.client,
            attributes=attributes,
            member_filter=member_filter,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
        return members[self]
        # from .user import User

        # body = {
        #     "WsRestGetMembersRequest": {
        #         "subjectAttributeNames": attributes,
        #         "wsGroupLookups": [{"groupName": self.name}],
        #         "memberFilter": member_filter,
        #         "includeSubjectDetail": "T",
        #     }
        # }
        # r = call_grouper(
        #     self.client,
        #     "/groups",
        #     body,
        #     act_as_subject_id=act_as_subject_id,
        #     act_as_subject_identifier=act_as_subject_identifier,
        # )
        # result = r["WsGetMembersResults"]["results"][0]
        # r_attributes = r["WsGetMembersResults"]["subjectAttributeNames"]
        # members: list["Subject"] = []
        # if result["resultMetadata"]["success"] == "T":
        #     if "wsSubjects" in result:
        #         for subject in result["wsSubjects"]:
        #             if subject["sourceId"] == "g:gsa":
        #                 group = get_group_by_name(subject["name"], self.client)
        #                 members.append(group)
        #             else:
        #                 user = User.from_results(
        #                     client=self.client,
        #                     user_body=subject,
        #                     subject_attr_names=r_attributes,
        #                 )
        #                 members.append(user)
        #     else:
        #         pass
        # else:  # pragma: no cover
        #     raise Exception
        # return members

    # def get_groups(
    #     self, stem: str | None = None, substems: bool = True
    # ) -> list["Group"]:
    #     return get_groups_for_subject(self.id, self.client, stem, substems)

    def create_privilege(
        self,
        entity_identifier: str,
        privilege_name: str,
    ) -> None:
        assign_privilege(
            target=self.name,
            target_type="group",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="T",
            client=self.client,
        )

    def delete_privilege(
        self,
        entity_identifier: str,
        privilege_name: str,
    ) -> None:
        assign_privilege(
            target=self.name,
            target_type="group",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="F",
            client=self.client,
        )

    def add_members(
        self,
        subject_identifiers: list[str] = [],
        subject_ids: list[str] = [],
        replace_all_existing: str = "F",
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> None:
        add_members_to_group(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
            replace_all_existing=replace_all_existing,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def delete_members(
        self,
        subject_identifiers: list[str] = [],
        subject_ids: list[str] = [],
    ) -> None:
        delete_members_from_group(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
        )

    def has_members(
        self,
        subject_identifiers: list[str] = [],
        subject_ids: list[str] = [],
        member_filter: str = "all",
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> dict[str, "HasMember"]:
        return has_members(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
            member_filter=member_filter,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )


def get_group_by_name(
    group_name: str,
    client: httpx.Client,
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> Group:
    body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": group_name,
            "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
            "includeGroupDetail": "T",
        }
    }
    r = call_grouper(
        client,
        "/groups",
        body,
        act_as_subject_id=act_as_subject_id,
        act_as_subject_identifier=act_as_subject_identifier,
    )
    if "groupResults" not in r["WsFindGroupsResults"]:
        raise GrouperGroupNotFoundException(group_name)
    return Group.from_results(client, r["WsFindGroupsResults"]["groupResults"][0])


def find_group_by_name(
    group_name: str,
    client: httpx.Client,
    stem: str | None = None,
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> list[Group]:
    body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": group_name,
            "queryFilterType": "FIND_BY_GROUP_NAME_APPROXIMATE",
            "includeGroupDetail": "T",
        }
    }
    if stem:
        body["WsRestFindGroupsLiteRequest"]["stemName"] = stem
    try:
        r = call_grouper(
            client,
            "/groups",
            body,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        r_metadata = r["WsFindGroupsResults"]["resultMetadata"]
        if r_metadata["resultCode"] == "INVALID_QUERY" and r_metadata[
            "resultMessage"
        ].startswith("Cant find stem"):
            raise GrouperStemNotFoundException(str(stem))
        else:  # pragma: no cover
            raise
    if "groupResults" in r["WsFindGroupsResults"]:
        return [
            Group.from_results(client, grp)
            for grp in r["WsFindGroupsResults"]["groupResults"]
        ]
    else:
        return []


def create_group(
    group_name: str,
    display_extension: str,
    description: str,
    client: httpx.Client,
    detail: dict[str, Any] | None = None,
) -> Group:
    group_to_save: dict[str, Any] = {
        "wsGroup": {
            "description": description,
            "displayExtension": display_extension,
            "name": group_name,
        },
        "wsGroupLookup": {"groupName": group_name},
    }
    if detail:  # pragma: no cover
        group_to_save["wsGroup"]["detail"] = detail
    body = {
        "WsRestGroupSaveRequest": {
            "wsGroupToSaves": [group_to_save],
            "includeGroupDetail": "T",
        }
    }
    r = call_grouper(client, "/groups", body)
    return Group.from_results(client, r["WsGroupSaveResults"]["results"][0]["wsGroup"])


def add_members_to_group(
    group_name: str,
    client: httpx.Client,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
    replace_all_existing: str = "F",
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> Group:
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
        r = call_grouper(
            client,
            "/groups",
            body,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
        return Group.from_results(client, r["WsAddMemberResults"]["wsGroupAssigned"])
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


def delete_members_from_group(
    group_name: str,
    client: httpx.Client,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
) -> None:
    identifiers_to_delete = [
        {"subjectIdentifier": ident} for ident in subject_identifiers
    ]
    ids_to_delete = [{"subjectId": sid} for sid in subject_ids]
    subjects_to_delete = identifiers_to_delete + ids_to_delete
    body = {
        "WsRestAddMemberRequest": {
            "subjectLookups": subjects_to_delete,
            "wsGroupLookup": {"groupName": group_name},
        }
    }
    call_grouper(client, "/groups", body)


def get_members_for_groups(
    groups: list[Group],
    client: httpx.Client,
    attributes: list[str] = [],
    member_filter: str = "all",
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> dict[Group, list[Subject]]:
    from .user import User

    group_lookup = [{"groupName": group.name} for group in groups]
    body = {
        "WsRestGetMembersRequest": {
            "subjectAttributeNames": attributes,
            "wsGroupLookups": group_lookup,
            "memberFilter": member_filter,
            "includeSubjectDetail": "T",
        }
    }
    r = call_grouper(
        client,
        "/groups",
        body,
        act_as_subject_id=act_as_subject_id,
        act_as_subject_identifier=act_as_subject_identifier,
    )
    r_dict: dict[Group, list[Subject]] = {}
    r_attributes = r["WsGetMembersResults"]["subjectAttributeNames"]
    for result in r["WsGetMembersResults"]["results"]:
        members: list["Subject"] = []
        key = Group.from_results(client, result["wsGroup"])
        if result["resultMetadata"]["success"] == "T":
            if "wsSubjects" in result:
                for subject in result["wsSubjects"]:
                    if subject["sourceId"] == "g:gsa":
                        group = get_group_by_name(subject["name"], client)
                        members.append(group)
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


class HasMember(Enum):
    IS_MEMBER = 1
    IS_NOT_MEMBER = 2
    SUBJECT_NOT_FOUND = 3


def has_members(
    group_name: str,
    client: httpx.Client,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
    member_filter: str = "all",
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> dict[str, HasMember]:
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
        r = call_grouper(
            client,
            f"/groups/{group_name}/members",
            body,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        if (
            r["WsHasMemberResults"]["resultMetadata"]["resultCode"]
            == "GROUP_NOT_FOUND"
        ):
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
