from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .group import Group
#     from .user import User

import httpx
from typing import Any
from copy import deepcopy
# from .group import Group
# from .user import User
# from .util_group import get_group_by_name
# from .group import Group


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
                body[request_type][
                    "actAsSubjectIdentifier"
                ] = act_as_subject_identifier
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
    data: dict[str, Any] = result.json()
    return data


# def get_group_by_name(
#     group_name: str,
#     client: httpx.Client
# ) -> Group:
#     body = {
#         "WsRestFindGroupsLiteRequest": {
#             "groupName": group_name,
#             "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
#             "includeGroupDetail": "T",
#         }
#     }
#     r = call_grouper(client, '/groups', body)
#     return Group(client, r["WsFindGroupsResults"]["groupResults"][0])


# def find_group_by_name(
#     group_name: str,
#     client: httpx.Client,
#     stem: str | None = None
# ) -> list[Group]:
#     body = {
#         "WsRestFindGroupsLiteRequest": {
#             "groupName": group_name,
#             "queryFilterType": "FIND_BY_GROUP_NAME_APPROXIMATE",
#             "includeGroupDetail": "T",
#         }
#     }
#     if stem:
#         body["WsRestFindGroupsLiteRequest"]['stemName'] = stem
#     r = call_grouper(client, '/groups', body)
#     return [
#         Group(client, grp) for
#         grp in r["WsFindGroupsResults"]["groupResults"]
#     ]


# def get_subject_by_identifier(
#     subject_identifier: str, client: httpx.Client
# ) -> User | Group:
#     body = {
#         "WsRestGetSubjectsLiteRequest": {
#             "subjectIdentifier": subject_identifier,
#             "includeSubjectDetail": "T",
#         }
#     }
#     r = call_grouper(client, "/subjects", body)
#     subject = r["WsGetSubjectsResults"]["wsSubjects"][0]
#     if subject["sourceId"] == "g:gsa":
#         return get_group_by_name(subject["name"], client)
#     else:
#         return User(
#             client=client,
#             user_body=subject,
#             subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
#         )


def get_groups_for_subject(
    subject_id: str,
    client: httpx.Client,
    stem: str | None = None,
    substems: bool = True
) -> list["Group"]:
    from .group import Group
    body = {
        "WsRestGetMembershipsRequest": {
            "fieldName": "members",
            "wsSubjectLookups": [{
                "subjectId": subject_id,
            }],
            "includeGroupDetail": "T",
        }
    }
    if stem:
        body['WsRestGetMembershipsRequest']['wsStemLookup'] = {
            'stemName': stem
        }
        if substems:
            body["WsRestGetMembershipsRequest"]['stemScope'] = 'ALL_IN_SUBTREE'
        else:
            body["WsRestGetMembershipsRequest"]['stemScope'] = 'ONE_LEVEL'
    r = call_grouper(client, "/memberships", body)
    return [
        Group(client, grp) for
        grp in r['WsGetMembershipsResults']['wsGroups']
    ]
