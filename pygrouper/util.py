from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .client import Client
    from .stem import Stem
    from .subject import Subject
    from .group import Group

import httpx
from copy import deepcopy
from .exceptions import (
    GrouperAuthException,
    GrouperSuccessException,
    GrouperSubjectNotFoundException,
    GrouperGroupNotFoundException,
    GrouperStemNotFoundException,
)


def call_grouper(
    client: httpx.Client,
    path: str,
    body: dict[str, Any],
    method: str = "POST",
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> dict[str, Any]:
    if act_as_subject_id or act_as_subject_identifier:
        if act_as_subject_id and act_as_subject_identifier:
            raise ValueError(
                "Only one of act_as_subject_id or "
                "act_as_subject_identifier should be specified"
            )
        body = deepcopy(body)
        request_type = list(body.keys())[0]
        lite = "Lite" in request_type
        if lite:
            if act_as_subject_id:
                body[request_type]["actAsSubjectId"] = act_as_subject_id
            else:
                body[request_type]["actAsSubjectIdentifier"] = act_as_subject_identifier
        else:
            if act_as_subject_id:
                body[request_type]["actAsSubjectLookup"] = {
                    "subjectId": act_as_subject_id
                }
            else:
                body[request_type]["actAsSubjectLookup"] = {
                    "subjectIdentifier": act_as_subject_identifier
                }

    result = client.request(method=method, url=path, json=body)
    print(result.status_code)
    if result.status_code == 401:
        raise GrouperAuthException(result.content)
    data: dict[str, Any] = result.json()
    result_type = list(data.keys())[0]
    if data[result_type]["resultMetadata"]["success"] != "T":
        raise GrouperSuccessException(data)
    return data


def get_stem_by_name(stem_name: str, client: Client) -> Stem:
    from .stem import Stem

    body = {
        "WsRestFindStemsLiteRequest": {
            "stemName": stem_name,
            "stemQueryFilterType": "FIND_BY_STEM_NAME",
            # "includeGroupDetail": "T",
        }
    }
    r = call_grouper(client.httpx_client, "/stems", body)
    return Stem.from_results(client, r["WsFindStemsResults"]["stemResults"][0])


def get_subject_by_identifier(
    subject_identifier: str,
    client: Client,
    resolve_group: bool = True,
    universal_id_attr: str = "description",
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> Subject:
    from .user import User

    body = {
        "WsRestGetSubjectsLiteRequest": {
            "subjectIdentifier": subject_identifier,
            "includeSubjectDetail": "T",
        }
    }
    r = call_grouper(
        client.httpx_client,
        "/subjects",
        body,
        act_as_subject_id=act_as_subject_id,
        act_as_subject_identifier=act_as_subject_identifier,
    )
    subject = r["WsGetSubjectsResults"]["wsSubjects"][0]
    if subject["success"] == "F":
        raise GrouperSubjectNotFoundException(subject_identifier)
    if subject["sourceId"] == "g:gsa":
        if resolve_group:
            # from .group import get_group_by_name

            return get_group_by_name(subject["name"], client)
        else:
            return Subject.from_results(
                client=client,
                subject_body=subject,
                subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
                universal_id_attr=universal_id_attr,
            )
    else:
        return User.from_results(
            client=client,
            user_body=subject,
            subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
            universal_id_attr=universal_id_attr,
        )


def get_group_by_name(
    group_name: str,
    client: Client,
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> Group:
    from .group import Group

    body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": group_name,
            "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
            "includeGroupDetail": "T",
        }
    }
    r = call_grouper(
        client.httpx_client,
        "/groups",
        body,
        act_as_subject_id=act_as_subject_id,
        act_as_subject_identifier=act_as_subject_identifier,
    )
    if "groupResults" not in r["WsFindGroupsResults"]:
        raise GrouperGroupNotFoundException(group_name)
    return Group.from_results(client, r["WsFindGroupsResults"]["groupResults"][0])


def find_group_by_name(
    group_name: str,
    client: Client,
    stem: str | None = None,
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> list[Group]:
    from .group import Group

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
        r = call_grouper(
            client.httpx_client,
            "/groups",
            body,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
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
