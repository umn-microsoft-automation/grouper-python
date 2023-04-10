from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .group import Group
    from .user import User
    from .stem import Stem
import httpx
# from typing import Any
# from copy import deepcopy
# from .util_group import get_group_by_name, find_group_by_name
from .stem import get_stem_by_name
# from .util import call_grouper
# from .util_user import get_subject_by_identifier
from .user import get_subject_by_identifier
from .group import get_group_by_name, find_group_by_name


class Client:
    def __init__(self, grouper_base_url: str, username: str, password: str) -> None:
        self.client = httpx.Client(
            auth=httpx.BasicAuth(username=username, password=password),
            base_url=grouper_base_url
        )

    # def call_grouper(
    #     self,
    #     path: str,
    #     body: dict[str, Any],
    #     method: str = "POST",
    #     act_as_subject_id: str | None = None,
    #     act_as_subject_identifier: str | None = None,
    # ) -> dict[str, Any]:
    #     if act_as_subject_id or act_as_subject_identifier:
    #         if act_as_subject_id and act_as_subject_identifier:
    #             raise ValueError(
    #                 "Only one of act_as_subject_id or "
    #                 "act_as_subject_identifier should be specified"
    #             )
    #         body = deepcopy(body)
    #         request_type = list(body.keys())[0]
    #         lite = "Lite" in request_type
    #         if lite:
    #             if act_as_subject_id:
    #                 body[request_type]["actAsSubjectId"] = act_as_subject_id
    #             else:
    #                 body[request_type][
    #                     "actAsSubjectIdentifier"
    #                 ] = act_as_subject_identifier
    #         else:
    #             if act_as_subject_id:
    #                 body[request_type]["actAsSubjectLookup"] = {
    #                     "subjectId": act_as_subject_id
    #                 }
    #             else:
    #                 body[request_type]["actAsSubjectLookup"] = {
    #                     "subjectIdentifier": act_as_subject_identifier
    #                 }

    #     result = self.client.request(method=method, url=path, json=body)
    #     data: dict[str, Any] = result.json()
    #     return data

    def get_group(
        self,
        group_name: str

    ) -> "Group":
        return get_group_by_name(group_name, self.client)
        # body = {
        #     "WsRestFindGroupsLiteRequest": {
        #         "groupName": group_id,
        #         "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
        #         "includeGroupDetail": "T",
        #     }
        # }
        # r = call_grouper(self.client, '/groups', body)
        # return Group(self.client, r["WsFindGroupsResults"]["groupResults"][0])

    def get_groups(
        self,
        group_name: str,
        stem: str | None = None
    ) -> list["Group"]:
        return find_group_by_name(
            group_name=group_name,
            client=self.client,
            stem=stem
        )

    def get_stem(
        self,
        stem_name: str
    ) -> "Stem":
        return get_stem_by_name(stem_name, self.client)

    def get_subject(
        self,
        subject_identifier: str
    ) -> Union["User", "Group"]:
        return get_subject_by_identifier(subject_identifier, self.client)
