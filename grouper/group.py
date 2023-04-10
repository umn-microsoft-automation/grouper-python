from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .user import User

import httpx
from .util import call_grouper, get_groups_for_subject
# from .util_group import get_group_by_name
# from .user import User
# import json
# from typing import Any
# from collections import namedtuple


class Group:
    def __init__(self, client: httpx.Client, group_body: dict[str, str]) -> None:
        self.client = client
        self.extension = group_body['extension']
        self.displayName = group_body['displayName']
        self.description = group_body['description']
        self.uuid = group_body['uuid']
        self.enabled = group_body['enabled']
        self.displayExtension = group_body['displayExtension']
        self.name = group_body['name']
        self.typeOfGroup = group_body['typeOfGroup']
        self.idIndex = group_body['idIndex']
        self.detail = group_body.get('detail')

    def __repr__(self) -> str:
        return f"<Grouper Group {self.name}>"

    def get_members(
        self,
        attributes: list[str] = [],
        member_filter: str = 'all',
    ) -> list[Union["User", "Group"]]:
        from .user import User
        body = {
            "WsRestGetMembersRequest": {
                "subjectAttributeNames": attributes,
                "wsGroupLookups": [{"groupName": self.name}],
                "memberFilter": member_filter,
                # "includeGroupDetail": "T",
                "includeSubjectDetail": "T"
            }
        }
        r = call_grouper(self.client, "/groups", body)
        # print(json.dumps(r))
        if r["WsGetMembersResults"]["resultMetadata"]["success"] != "T":
            raise Exception
        result = r["WsGetMembersResults"]["results"][0]
        r_attributes = r["WsGetMembersResults"]["subjectAttributeNames"]
        members: list[User | Group] = []
        # fields = set(['sourceId', 'id', 'memberId'] + r_attributes)
        # User = namedtuple('User', list(fields))
        if result["resultMetadata"]["success"] == "T":
            if "wsSubjects" in result:
                for subject in result["wsSubjects"]:
                    if subject['sourceId'] == 'g:gsa':
                        group = get_group_by_name(subject['name'], self.client)
                        members.append(group)
                    else:
                        user = User(
                            client=self.client,
                            user_body=subject,
                            subject_attr_names=r_attributes
                        )
                        # user = {
                        #     'sourceId': subject["sourceId"],
                        #     'id': subject["id"],
                        #     'memberId': subject['memberId']
                        # }
                        # for n in range(len(r_attributes)):
                        #     user[r_attributes[n]] = subject["attributeValues"][n]
                        # # r_user = User(**user)
                        members.append(user)
                # members = [
                #     subject["attributeValues"][0]
                #     for subject in result["wsSubjects"]
                #     # if subject["attributeValues"][0]
                #     # != f'{subject["id"]} entity not found'
                # ]
            else:
                pass
        else:  # pragma: no cover
            raise Exception
        return members

    def get_groups(
        self,
        stem: str | None = None,
        substems: bool = True
    ) -> list["Group"]:
        return get_groups_for_subject(self.id, self.client, stem, substems)


def get_group_by_name(
    group_name: str,
    client: httpx.Client
) -> Group:
    body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": group_name,
            "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
            "includeGroupDetail": "T",
        }
    }
    r = call_grouper(client, '/groups', body)
    return Group(client, r["WsFindGroupsResults"]["groupResults"][0])


def find_group_by_name(
    group_name: str,
    client: httpx.Client,
    stem: str | None = None
) -> list[Group]:
    body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": group_name,
            "queryFilterType": "FIND_BY_GROUP_NAME_APPROXIMATE",
            "includeGroupDetail": "T",
        }
    }
    if stem:
        body["WsRestFindGroupsLiteRequest"]['stemName'] = stem
    r = call_grouper(client, '/groups', body)
    return [
        Group(client, grp) for
        grp in r["WsFindGroupsResults"]["groupResults"]
    ]
