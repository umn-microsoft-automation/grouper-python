from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .group import Group
import httpx
from .util import call_grouper
from .privilege import assign_privilege
from .group import create_group


class Stem:
    def __init__(self, client: httpx.Client, stem_body: dict[str, str]) -> None:
        self.client = client
        self.displayExtension = stem_body['displayExtension']
        self.extension = stem_body['extension']
        self.displayName = stem_body['displayName']
        self.name = stem_body['name']
        self.description = stem_body.get('description', "")
        self.idIndex = stem_body['idIndex']
        self.uuid = stem_body['uuid']
        self.id = self.uuid

    def create_privilege(
        self,
        entity_identifier: str,
        privilege_name: str,
    ) -> None:
        assign_privilege(
            target=self.name,
            target_type="stem",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="T",
            client=self.client
        )

    def delete_privilege(
        self,
        entity_identifier: str,
        privilege_name: str,
    ) -> None:
        assign_privilege(
            target=self.name,
            target_type="stem",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="F",
            client=self.client
        )

    def create_child_stem(
        self,
        extension: str,
        display_extension: str,
        description: str = ""
    ) -> "Stem":
        return create_stem(
            stem_name=f"{self.name}:{extension}",
            display_extension=display_extension,
            description=description,
            client=self.client
        )

    def create_child_group(
        self,
        extension: str,
        display_extension: str,
        description: str = "",
        detail: dict[str, Any] | None = None,
    ) -> "Group":
        return create_group(
            group_name=f"{self.name}:{extension}",
            display_extension=display_extension,
            description=description,
            detail=detail,
            client=self.client
        )


def get_stem_by_name(
    stem_name: str,
    client: httpx.Client
) -> Stem:
    body = {
        "WsRestFindStemsLiteRequest": {
            "stemName": stem_name,
            "stemQueryFilterType": "FIND_BY_STEM_NAME",
            # "includeGroupDetail": "T",
        }
    }
    r = call_grouper(client, '/stems', body)
    return Stem(client, r['WsFindStemsResults']['stemResults'][0])


def create_stem(
    stem_name: str,
    display_extension: str,
    description: str,
    client: httpx.Client
) -> Stem:
    body = {
        "WsRestStemSaveLiteRequest": {
            "description": description,
            "stemName": stem_name,
            "displayExtension": display_extension,
        }
    }
    r = call_grouper(client, f'/stems/{stem_name}', body)
    return Stem(client, r['WsStemSaveLiteResult']['wsStem'])
