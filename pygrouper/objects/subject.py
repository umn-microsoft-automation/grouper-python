from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .group import Group
    # from .client import Client
    from .membership import HasMember

from .client import Client
from pydantic import BaseModel

from ..subject import get_groups_for_subject
from ..membership import has_members


class Subject(BaseModel):
    # from .client import Client
    # extension: str
    # displayName: str
    id: str
    description: str = ""
    universal_id: str
    # uuid: str
    # enabled: str
    # displayExtension: str
    # name: str
    # typeOfGroup: str
    # idIndex: str
    # detail: dict[str, Any] | None
    client: Client

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_results(
        cls: type[Subject],
        client: Client,
        subject_body: dict[str, Any],
        subject_attr_names: list[str],
        universal_id_attr: str = "description",
    ) -> Subject:
        attrs = {
            subject_attr_names[i]: subject_body["attributeValues"][i]
            for i in range(len(subject_attr_names))
        }
        return cls(
            id=subject_body["id"],
            description=subject_body.get("description", ""),
            universal_id=attrs.get(universal_id_attr, ""),
            client=client,
        )

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
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> list[Group]:
        return get_groups_for_subject(
            self.id,
            self.client,
            stem,
            substems,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def is_member(
        self,
        group_name: str,
        member_filter: str = "all",
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> bool:
        from .membership import HasMember

        result = has_members(
            group_name=group_name,
            client=self.client,
            subject_ids=[self.id],
            member_filter=member_filter,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
        if result[self.id] == HasMember.IS_MEMBER:
            return True
        elif result[self.id] == HasMember.IS_NOT_MEMBER:
            return False
        else:
            raise ValueError