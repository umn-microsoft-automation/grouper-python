from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .group import Group
    from .privilege import Privilege
    from .client import GrouperClient
from ..subject import get_groups_for_subject
from ..membership import has_members
from ..privilege import get_privileges


class Subject:
    def __init__(
        self,
        client: GrouperClient,
        subject_body: dict[str, Any],
        subject_attr_names: list[str],
    ) -> None:
        attrs = {
            subject_attr_names[i]: subject_body["attributeValues"][i]
            for i in range(len(subject_attr_names))
        }
        if subject_body["sourceId"] == "g:gsa":
            universal_identifier_attr = "name"
        else:
            universal_identifier_attr = client.universal_identifier_attr
        self.id: str = subject_body["id"]
        self.description: str = attrs.get("description", "")
        self.universal_identifier: str = attrs[universal_identifier_attr]
        self.sourceId: str = subject_body["sourceId"]
        self.name: str = subject_body["name"]
        self.client = client

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Subject):
            return NotImplemented
        return self.id == other.id

    def get_groups(
        self,
        stem: str | None = None,
        substems: bool = True,
        act_as_subject: Subject | None = None,
    ) -> list[Group]:
        return get_groups_for_subject(
            self.id,
            self.client,
            stem,
            substems,
            act_as_subject=act_as_subject,
        )

    def is_member(
        self,
        group_name: str,
        member_filter: str = "all",
        act_as_subject: Subject | None = None,
    ) -> bool:
        from .membership import HasMember

        result = has_members(
            group_name=group_name,
            client=self.client,
            subject_ids=[self.id],
            member_filter=member_filter,
            act_as_subject=act_as_subject,
        )
        if result[self.id] == HasMember.IS_MEMBER:
            return True
        elif result[self.id] == HasMember.IS_NOT_MEMBER:
            return False
        else:
            raise ValueError

    def get_privileges_for_this(
        self,
        group_name: str | None = None,
        stem_name: str | None = None,
        privilege_name: str | None = None,
        privilege_type: str | None = None,
        attributes: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> list[Privilege]:
        return get_privileges(
            client=self.client,
            subject_id=self.id,
            group_name=group_name,
            stem_name=stem_name,
            privilege_name=privilege_name,
            privilege_type=privilege_type,
            attributes=attributes,
            act_as_subject=act_as_subject,
        )
