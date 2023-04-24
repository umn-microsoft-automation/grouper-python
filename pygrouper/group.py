from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .objects.group import CreateGroup, Group
    from .objects.client import Client
    from .objects.subject import Subject
from .objects.exceptions import (
    GrouperGroupNotFoundException,
    GrouperSuccessException,
    GrouperStemNotFoundException,
)


def find_group_by_name(
    group_name: str,
    client: Client,
    stem: str | None = None,
    act_as_subject: Subject | None = None,
) -> list[Group]:
    from .objects.group import Group

    body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": group_name,
            "queryFilterType": "FIND_BY_GROUP_NAME_APPROXIMATE",
            "includeGroupDetail": "T",
        }
    }
    if stem:
        body["WsRestFindGroupsLiteRequest"]["stemName"] = stem
    try:
        r = client._call_grouper(
            "/groups",
            body,
            act_as_subject=act_as_subject,
        )
    except GrouperSuccessException as err:
        r = err.grouper_result
        r_metadata = r["WsFindGroupsResults"]["resultMetadata"]
        if r_metadata["resultCode"] == "INVALID_QUERY" and r_metadata[
            "resultMessage"
        ].startswith("Cant find stem"):
            raise GrouperStemNotFoundException(str(stem))
        else:  # pragma: no cover
            raise
    if "groupResults" in r["WsFindGroupsResults"]:
        return [
            Group.from_results(client, grp)
            for grp in r["WsFindGroupsResults"]["groupResults"]
        ]
    else:
        return []


def create_groups(
    groups: list[CreateGroup],
    client: Client,
    act_as_subject: Subject | None = None,
) -> list[Group]:
    from .objects.group import Group

    groups_to_save = []
    for group in groups:
        group_to_save: dict[str, Any] = {
            "wsGroup": {
                "description": group.description,
                "displayExtension": group.display_extension,
                "name": group.name,
            },
            "wsGroupLookup": {"groupName": group.name},
        }
        if group.detail:
            group_to_save["wsGroup"]["detail"] = group.detail
        groups_to_save.append(group_to_save)
    body = {
        "WsRestGroupSaveRequest": {
            "wsGroupToSaves": group_to_save,
            "includeGroupDetail": "T",
        }
    }
    r = client._call_grouper(
        "/groups",
        body,
        act_as_subject=act_as_subject,
    )
    return [
        Group.from_results(client, result["wsGroup"])
        for result in r["WsGroupSaveResults"]["results"]
    ]


def delete_groups(
    group_names: list[str],
    client: Client,
    act_as_subject: Subject | None = None,
) -> None:
    group_lookup = [{"groupName": group} for group in group_names]
    body = {
        "WsRestGroupDeleteRequest": {
            "wsGroupLookups": group_lookup,
        }
    }
    r = client._call_grouper(
        "/groups",
        body,
        act_as_subject=act_as_subject,
    )
    for result in r["WsGroupDeleteResults"]["results"]:
        if result["resultMetadata"]["resultCode"] != "SUCCESS":
            raise GrouperSuccessException(r)


def get_groups_by_parent(
    parent_name: str,
    client: Client,
    recursive: bool = False,
    act_as_subject: Subject | None = None,
) -> list[Group]:
    from .objects.group import Group

    body = {
        "WsRestFindGroupsLiteRequest": {
            "stemName": parent_name,
            "queryFilterType": "FIND_BY_STEM_NAME",
        }
    }
    if recursive:
        body["WsRestFindGroupsLiteRequest"]["parentStemNameScope"] = "ALL_IN_SUBTREE"
    else:
        body["WsRestFindGroupsLiteRequest"]["parentStemNameScope"] = "ONE_LEVEL"
    r = client._call_grouper(
        "/groups",
        body,
        act_as_subject=act_as_subject,
    )
    print(r)
    if "groupResults" in r["WsFindGroupsResults"]:
        return [
            Group.from_results(client, grp)
            for grp in r["WsFindGroupsResults"]["groupResults"]
        ]
    else:
        return []


def get_group_by_name(
    group_name: str,
    client: Client,
    act_as_subject: Subject | None = None,
) -> Group:
    from .objects.group import Group

    body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": group_name,
            "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
            "includeGroupDetail": "T",
        }
    }
    r = client._call_grouper("/groups", body, act_as_subject=act_as_subject)
    if "groupResults" not in r["WsFindGroupsResults"]:
        raise GrouperGroupNotFoundException(group_name)
    return Group.from_results(client, r["WsFindGroupsResults"]["groupResults"][0])
