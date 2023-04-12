from typing import TYPE_CHECKING, Union, Any

if TYPE_CHECKING:
    from .user import User

import httpx
from .util import call_grouper
from .subject import get_groups_for_subject
from .privilege import assign_privilege


class Group:
    def __init__(self, client: httpx.Client, group_body: dict[str, Any]) -> None:
        self.client = client
        self.extension = group_body["extension"]
        self.displayName = group_body["displayName"]
        self.description = group_body.get("description", "")
        self.uuid = group_body["uuid"]
        self.id = self.uuid
        self.enabled = group_body["enabled"]
        self.displayExtension = group_body["displayExtension"]
        self.name = group_body["name"]
        self.typeOfGroup = group_body["typeOfGroup"]
        self.idIndex = group_body["idIndex"]
        self.detail: dict[str, Any] | None = group_body.get("detail")

    def __repr__(self) -> str:
        return f"<Grouper Group {self.name}>"

    def get_members(
        self,
        attributes: list[str] = [],
        member_filter: str = "all",
    ) -> list[Union["User", "Group"]]:
        from .user import User

        body = {
            "WsRestGetMembersRequest": {
                "subjectAttributeNames": attributes,
                "wsGroupLookups": [{"groupName": self.name}],
                "memberFilter": member_filter,
                "includeSubjectDetail": "T",
            }
        }
        r = call_grouper(self.client, "/groups", body)
        if r["WsGetMembersResults"]["resultMetadata"]["success"] != "T":
            raise Exception
        result = r["WsGetMembersResults"]["results"][0]
        r_attributes = r["WsGetMembersResults"]["subjectAttributeNames"]
        members: list[User | Group] = []
        if result["resultMetadata"]["success"] == "T":
            if "wsSubjects" in result:
                for subject in result["wsSubjects"]:
                    if subject["sourceId"] == "g:gsa":
                        group = get_group_by_name(subject["name"], self.client)
                        members.append(group)
                    else:
                        user = User(
                            client=self.client,
                            user_body=subject,
                            subject_attr_names=r_attributes,
                        )
                        members.append(user)
            else:
                pass
        else:  # pragma: no cover
            raise Exception
        return members

    def get_groups(
        self, stem: str | None = None, substems: bool = True
    ) -> list["Group"]:
        return get_groups_for_subject(self.id, self.client, stem, substems)

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
    ) -> None:
        add_members_to_group(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
            replace_all_existing=replace_all_existing,
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


def get_group_by_name(group_name: str, client: httpx.Client) -> Group:
    body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": group_name,
            "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
            "includeGroupDetail": "T",
        }
    }
    r = call_grouper(client, "/groups", body)
    return Group(client, r["WsFindGroupsResults"]["groupResults"][0])


def find_group_by_name(
    group_name: str, client: httpx.Client, stem: str | None = None
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
    r = call_grouper(client, "/groups", body)
    return [Group(client, grp) for grp in r["WsFindGroupsResults"]["groupResults"]]


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
    return Group(client, r["WsGroupSaveResults"]["results"][0]["wsGroup"])


def add_members_to_group(
    group_name: str,
    client: httpx.Client,
    subject_identifiers: list[str] = [],
    subject_ids: list[str] = [],
    replace_all_existing: str = "F",
) -> None:
    identifiers_to_add = [{"subjectIdentifier": ident} for ident in subject_identifiers]
    ids_to_add = [{"subjectId": sid} for sid in subject_ids]
    subjects_to_add = identifiers_to_add + ids_to_add
    body = {
        "WsRestAddMemberRequest": {
            "subjectLookups": subjects_to_add,
            "wsGroupLookup": {"groupName": group_name},
            "replaceAllExisting": replace_all_existing,
        }
    }
    call_grouper(client, "/groups", body)


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
