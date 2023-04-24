from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .membership import Membership, HasMember
    from .client import Client
from .subject import Subject
# from .client import Client
from pydantic import BaseModel
from ..membership import (
    get_members_for_groups,
    get_memberships_for_groups,
    add_members_to_group,
    delete_members_from_group,
    has_members,
)
from ..privilege import assign_privilege
from ..group import delete_groups


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
        cls: type[Group],
        client: Client,
        group_body: dict[str, Any],
        subject_attr_names: list[str] = [],
    ) -> Group:
        return cls(
            id=group_body["uuid"],
            description=group_body.get("description", ""),
            universal_identifier=group_body["name"],
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
        resolve_groups: bool = True,
        act_as_subject: Subject | None = None,
    ) -> list[Subject]:
        members = get_members_for_groups(
            group_names=[self.name],
            client=self.client,
            attributes=attributes,
            member_filter=member_filter,
            resolve_groups=resolve_groups,
            act_as_subject=act_as_subject,
        )
        return members[self]

    def get_memberships(
        self,
        attributes: list[str] = [],
        member_filter: str = "all",
        resolve_groups: bool = True,
        act_as_subject: Subject | None = None,
    ) -> list[Membership]:
        memberships = get_memberships_for_groups(
            group_names=[self.name],
            client=self.client,
            attributes=attributes,
            member_filter=member_filter,
            resolve_groups=resolve_groups,
            act_as_subject=act_as_subject,
        )
        return memberships[self]

    def create_privilege(
        self,
        entity_identifier: str,
        privilege_name: str,
        act_as_subject: Subject | None = None,
    ) -> None:
        assign_privilege(
            target=self.name,
            target_type="group",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="T",
            client=self.client,
            act_as_subject=act_as_subject
        )

    def delete_privilege(
        self,
        entity_identifier: str,
        privilege_name: str,
        act_as_subject: Subject | None = None,
    ) -> None:
        assign_privilege(
            target=self.name,
            target_type="group",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="F",
            client=self.client,
            act_as_subject=act_as_subject,
        )

    def add_members(
        self,
        subject_identifiers: list[str] = [],
        subject_ids: list[str] = [],
        replace_all_existing: str = "F",
        act_as_subject: Subject | None = None,
    ) -> None:
        add_members_to_group(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
            replace_all_existing=replace_all_existing,
            act_as_subject=act_as_subject,
        )

    def delete_members(
        self,
        subject_identifiers: list[str] = [],
        subject_ids: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> None:
        delete_members_from_group(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
            act_as_subject=act_as_subject,
        )

    def has_members(
        self,
        subject_identifiers: list[str] = [],
        subject_ids: list[str] = [],
        member_filter: str = "all",
        act_as_subject: Subject | None = None,
    ) -> dict[str, HasMember]:
        return has_members(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
            member_filter=member_filter,
            act_as_subject=act_as_subject,
        )

    def delete(
        self,
        act_as_subject: Subject | None = None,
    ) -> None:
        delete_groups(
            group_names=[self.name],
            client=self.client,
            act_as_subject=act_as_subject,
        )


class CreateGroup(BaseModel):
    name: str
    display_extension: str
    description: str
    detail: dict[str, Any] | None = None
