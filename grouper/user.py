from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .group import Group
    # from .user import User

import httpx
from .group import get_group_by_name
from .util import call_grouper, get_groups_for_subject

# import json
# from typing import Any
# from collections import namedtuple


class User:
    def __init__(
        self,
        client: httpx.Client,
        user_body: dict[str, str],
        subject_attr_names: list[str],
    ) -> None:
        self.client = client
        self.sourceId = user_body["sourceId"]
        self.name = user_body["name"]
        self.id = user_body["id"]
        attrs = {}
        for n in range(len(subject_attr_names)):
            attrs[subject_attr_names[n]] = user_body["attributeValues"][n]
        self.attributes = attrs
        self.description = attrs["description"]
        # self.description = group_body['description']
        # self.uuid = group_body['uuid']
        # self.enabled = group_body['enabled']
        # self.displayExtension = group_body['displayExtension']
        # self.name = group_body['name']
        # self.typeOfGroup = group_body['typeOfGroup']
        # self.idIndex = group_body['idIndex']
        # self.detail = group_body.get('detail')

    def get_groups(
        self,
        stem: str | None = None,
        substems: bool = True
    ) -> list["Group"]:
        return get_groups_for_subject(self.id, self.client, stem, substems)

    # def get_members(
    #     self,
    #     attributes: list[str] = [],
    #     member_filter: str = 'all',
    # ) -> list[dict[str, str]]:
    #     body = {
    #         "WsRestGetMembersRequest": {
    #             "subjectAttributeNames": attributes,
    #             "wsGroupLookups": [{"groupName": self.name}],
    #             "memberFilter": member_filter,
    #             # "includeGroupDetail": "T",
    #             "includeSubjectDetail": "T"
    #         }
    #     }
    #     r = call_grouper(self.client, "/groups", body)
    #     # print(json.dumps(r))
    #     if r["WsGetMembersResults"]["resultMetadata"]["success"] != "T":
    #         raise Exception
    #     result = r["WsGetMembersResults"]["results"][0]
    #     r_attributes = r["WsGetMembersResults"]["subjectAttributeNames"]
    #     members = []
    #     # fields = set(['sourceId', 'id', 'memberId'] + r_attributes)
    #     # User = namedtuple('User', list(fields))
    #     if result["resultMetadata"]["success"] == "T":
    #         if "wsSubjects" in result:
    #             for subject in result["wsSubjects"]:
    #                 user = {
    #                     'sourceId': subject["sourceId"],
    #                     'id': subject["id"],
    #                     'memberId': subject['memberId']
    #                 }
    #                 for n in range(len(r_attributes)):
    #                     user[r_attributes[n]] = subject["attributeValues"][n]
    #                 # r_user = User(**user)
    #                 members.append(user)
    #             # members = [
    #             #     subject["attributeValues"][0]
    #             #     for subject in result["wsSubjects"]
    #             #     # if subject["attributeValues"][0]
    #             #     # != f'{subject["id"]} entity not found'
    #             # ]
    #         else:
    #             pass
    #     else:  # pragma: no cover
    #         raise Exception
    #     return members


def get_subject_by_identifier(
    subject_identifier: str, client: httpx.Client
) -> Union[User, "Group"]:
    body = {
        "WsRestGetSubjectsLiteRequest": {
            "subjectIdentifier": subject_identifier,
            "includeSubjectDetail": "T",
        }
    }
    r = call_grouper(client, "/subjects", body)
    subject = r["WsGetSubjectsResults"]["wsSubjects"][0]
    if subject["sourceId"] == "g:gsa":
        return get_group_by_name(subject["name"], client)
    else:
        return User(
            client=client,
            user_body=subject,
            subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
        )
