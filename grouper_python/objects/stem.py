from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .subject import Subject
    from .group import Group
    from .privilege import Privilege

from ..privilege import assign_privilege, get_privileges
from ..stem import create_stems, get_stems_by_parent, delete_stems
from ..group import create_groups, get_groups_by_parent
from .client import GrouperClient
from dataclasses import dataclass


class Stem:
    def __init__(
        self,
        client: GrouperClient,
        stem_body: dict[str, Any],
        subject_attr_names: list[str] = [],
    ) -> None:
        self.id: str = stem_body["uuid"]
        self.description: str = stem_body.get("description", "")
        self.extension: str = stem_body["extension"]
        self.displayName: str = stem_body["displayName"]
        self.uuid: str = stem_body["uuid"]
        self.displayExtension: str = stem_body["displayExtension"]
        self.name: str = stem_body["name"]
        self.idIndex: str = stem_body["idIndex"]
        self.client = client

    def create_privilege_on_this(
        self,
        entity_identifier: str,
        privilege_name: str,
        act_as_subject: Subject | None = None,
    ) -> None:
        assign_privilege(
            target=self.name,
            target_type="stem",
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
            target_type="stem",
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
            stem_name=self.name,
            privilege_name=privilege_name,
            attributes=attributes,
            act_as_subject=act_as_subject,
        )

    def create_child_stem(
        self,
        extension: str,
        display_extension: str,
        description: str = "",
        act_as_subject: Subject | None = None,
    ) -> Stem:
        create = CreateStem(
            name=f"{self.name}:{extension}",
            displayExtension=display_extension,
            description=description,
        )
        return create_stems(
            [create],
            self.client,
            act_as_subject=act_as_subject,
        )[0]

    def create_child_group(
        self,
        extension: str,
        display_extension: str,
        description: str = "",
        detail: dict[str, Any] | None = None,
        act_as_subject: Subject | None = None,
    ) -> Group:
        from .group import CreateGroup

        create = CreateGroup(
            name=f"{self.name}:{extension}",
            display_extension=display_extension,
            description=description,
            detail=detail,
        )
        return (create_groups([create], self.client, act_as_subject))[0]

    def get_child_stems(
        self,
        recursive: bool,
        act_as_subject: Subject | None = None,
    ) -> list[Stem]:
        return get_stems_by_parent(
            parent_name=self.name,
            client=self.client,
            recursive=recursive,
            act_as_subject=act_as_subject,
        )

    def get_child_groups(
        self,
        recursive: bool,
        act_as_subject: Subject | None = None,
    ) -> list[Group]:
        return get_groups_by_parent(
            parent_name=self.name,
            client=self.client,
            recursive=recursive,
            act_as_subject=act_as_subject,
        )

    def delete(
        self,
        act_as_subject: Subject | None = None,
    ) -> None:
        delete_stems(
            stem_names=[self.name], client=self.client, act_as_subject=act_as_subject
        )


@dataclass
class CreateStem:
    name: str
    displayExtension: str
    description: str
