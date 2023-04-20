from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # from .client import Client
    from .group import Group

from pydantic import BaseModel
from ..privilege import assign_privilege
from ..stem import create_stems, get_stems_by_parent, delete_stems
from ..group import create_groups, get_groups_by_parent
from .client import Client


class Stem(BaseModel):
    client: Client
    displayExtension: str
    extension: str
    displayName: str
    name: str
    description: str
    idIndex: str
    uuid: str
    id: str
    # def __init__(self, client: httpx.Client, stem_body: dict[str, str]) -> None:
    #     self.client = client
    #     self.displayExtension = stem_body["displayExtension"]
    #     self.extension = stem_body["extension"]
    #     self.displayName = stem_body["displayName"]
    #     self.name = stem_body["name"]
    #     self.description = stem_body.get("description", "")
    #     self.idIndex = stem_body["idIndex"]
    #     self.uuid = stem_body["uuid"]
    #     self.id = self.uuid

    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def from_results(
        cls: type[Stem],
        client: Client,
        stem_body: dict[str, Any],
        subject_attr_names: list[str] = [],
        universal_id_attr: str = "description",
    ) -> Stem:
        return cls(
            id=stem_body["uuid"],
            description=stem_body.get("description", ""),
            extension=stem_body["extension"],
            displayName=stem_body["displayName"],
            uuid=stem_body["uuid"],
            displayExtension=stem_body["displayExtension"],
            name=stem_body["name"],
            idIndex=stem_body["idIndex"],
            client=client,
        )

    def create_privilege(
        self,
        entity_identifier: str,
        privilege_name: str,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> None:
        assign_privilege(
            target=self.name,
            target_type="stem",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="T",
            client=self.client,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def delete_privilege(
        self,
        entity_identifier: str,
        privilege_name: str,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> None:
        assign_privilege(
            target=self.name,
            target_type="stem",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="F",
            client=self.client,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def create_child_stem(
        self,
        extension: str,
        display_extension: str,
        description: str = "",
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> Stem:
        create = CreateStem(
            name=f"{self.name}:{extension}",
            displayExtension=display_extension,
            description=description,
        )
        return create_stems(
            [create],
            self.client,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )[0]

    def create_child_group(
        self,
        extension: str,
        display_extension: str,
        description: str = "",
        detail: dict[str, Any] | None = None,
    ) -> Group:
        from .group import CreateGroup

        create = CreateGroup(
            name=f"{self.name}:{extension}",
            display_extension=display_extension,
            description=description,
            detail=detail,
        )
        return (create_groups([create], self.client))[0]

    def get_child_stems(
        self,
        recursive: bool,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> list[Stem]:
        return get_stems_by_parent(
            parent_name=self.name,
            client=self.client,
            recursive=recursive,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def get_child_groups(
        self,
        recursive: bool,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> list[Group]:
        return get_groups_by_parent(
            parent_name=self.name,
            client=self.client,
            recursive=recursive,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def delete(
        self,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> None:
        delete_stems(
            stem_names=[self.name],
            client=self.client,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )


class CreateStem(BaseModel):
    name: str
    displayExtension: str
    description: str
