from __future__ import annotations
from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .group import Group
    # from .client import Client
    # from .membership import HasMember

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
    universal_identifier: str
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
    ) -> Subject:
        attrs = {
            subject_attr_names[i]: subject_body["attributeValues"][i]
            for i in range(len(subject_attr_names))
        }
        if subject_body["sourceId"] == "g:gsa":
            universal_identifier_attr = "name"
        else:
            universal_identifier_attr = client.universal_identifier_attr
        return cls(
            id=subject_body["id"],
            description=subject_body.get("description", ""),
            universal_identifier=attrs.get(universal_identifier_attr),
            client=client,
        )

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        # This method relies on "duck typing" so we silence a lot of mypy errors
        if isinstance(other, str):
            # If a string is passed, see if it matches the id or identifier
            return other == self.id or other == self.universal_identifier
        try:
            # Try and reference the id as an attribute
            return self.id == other.id  # type: ignore[no-any-return, attr-defined]
        except AttributeError:
            pass
        try:
            # Try and reference the id as a key
            return self.id == other["id"]  # type: ignore[no-any-return, index]
        except KeyError:
            pass
        # If we've gotten this far, we can't figure out how make a comparison
        return NotImplemented

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
