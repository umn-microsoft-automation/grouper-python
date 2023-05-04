from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .membership import Membership, HasMember
    from .client import GrouperClient
    from .privilege import Privilege
from .subject import Subject
from dataclasses import dataclass
from ..membership import (
    get_members_for_groups,
    get_memberships_for_groups,
    add_members_to_group,
    delete_members_from_group,
    has_members,
)
from ..privilege import assign_privilege, get_privileges
from ..group import delete_groups


class Group(Subject):
    """Group object representing a Grouper group."""

    def __init__(
        self,
        client: GrouperClient,
        group_body: dict[str, Any],
        subject_attr_names: list[str] = []
    ) -> None:
        self.id: str = group_body["uuid"]
        self.description: str = group_body.get("description", "")
        self.universal_identifier: str = group_body["name"]
        self.sourceId = "g:gsa"
        self.name: str = group_body["name"]
        self.extension: str = group_body["extension"]
        self.displayName: str = group_body["displayName"]
        self.uuid: str = group_body["uuid"]
        self.enabled: str = group_body["enabled"]
        self.displayExtension: str = group_body["displayExtension"]
        self.typeOfGroup: str = group_body["typeOfGroup"]
        self.idIndex: str = group_body["idIndex"]
        self.detail: dict[str, Any] | None = group_body.get("detail")
        self.client = client

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
        return memberships[self] if memberships else []

    def create_privilege_on_this(
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
            act_as_subject=act_as_subject,
        )

    def delete_privilege_on_this(
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

    def get_privilege_on_this(
        self,
        subject_id: str | None = None,
        subject_identifier: str | None = None,
        privilege_name: str | None = None,
        attributes: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> list[Privilege]:
        return get_privileges(
            client=self.client,
            subject_id=subject_id,
            subject_identifier=subject_identifier,
            group_name=self.name,
            privilege_name=privilege_name,
            attributes=attributes,
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


@dataclass
class CreateGroup:
    name: str
    display_extension: str
    description: str
    detail: dict[str, Any] | None = None
