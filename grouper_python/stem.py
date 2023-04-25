from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .objects.stem import Stem, CreateStem
    from .objects.client import Client
    from .objects.subject import Subject


def get_stem_by_name(
    stem_name: str, client: Client, act_as_subject: Subject | None = None
) -> Stem:
    from .objects.stem import Stem

    body = {
        "WsRestFindStemsLiteRequest": {
            "stemName": stem_name,
            "stemQueryFilterType": "FIND_BY_STEM_NAME",
            # "includeGroupDetail": "T",
        }
    }
    r = client._call_grouper("/stems", body, act_as_subject=act_as_subject)
    return Stem.from_results(client, r["WsFindStemsResults"]["stemResults"][0])


def get_stems_by_parent(
    parent_name: str,
    client: Client,
    recursive: bool = False,
    act_as_subject: Subject | None = None,
) -> list[Stem]:
    from .objects.stem import Stem

    body = {
        "WsRestFindStemsLiteRequest": {
            "parentStemName": parent_name,
            "stemQueryFilterType": "FIND_BY_PARENT_STEM_NAME",
        }
    }
    if recursive:
        body["WsRestFindStemsLiteRequest"]["parentStemNameScope"] = "ALL_IN_SUBTREE"
    else:
        body["WsRestFindStemsLiteRequest"]["parentStemNameScope"] = "ONE_LEVEL"
    r = client._call_grouper(
        "/stems",
        body,
        act_as_subject=act_as_subject,
    )
    return [
        Stem.from_results(client, stem)
        for stem in r["WsFindStemsResults"]["stemResults"]
    ]


def create_stems(
    creates: list[CreateStem],
    client: Client,
    act_as_subject: Subject | None = None,
) -> list[Stem]:
    from .objects.stem import Stem

    stems_to_save = [
        {
            "wsStem": {
                "displayExtension": stem.displayExtension,
                "name": stem.name,
                "description": stem.description,
            },
            "wsStemLookup": {"stemName": stem.name},
        }
        for stem in creates
    ]
    body = {
        "WsRestStemSaveRequest": {
            "wsStemToSaves": stems_to_save,
        }
    }
    r = client._call_grouper("/stems", body, act_as_subject=act_as_subject)
    return [
        Stem.from_results(client, result["wsStem"])
        for result in r["WsStemSaveResults"]["results"]
    ]


def delete_stems(
    stem_names: list[str],
    client: Client,
    act_as_subject: Subject | None = None,
) -> None:
    stem_lookups = [{"stemName": stem_name} for stem_name in stem_names]
    body = {"WsRestStemDeleteRequest": {"wsStemLookups": stem_lookups}}
    client._call_grouper("/stems", body, act_as_subject=act_as_subject)
