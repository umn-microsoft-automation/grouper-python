from typing import TYPE_CHECKING, Union
if TYPE_CHECKING:
    from .group import Group
    from .user import User
    from .stem import Stem
import httpx
from .stem import get_stem_by_name
from .user import get_subject_by_identifier
from .group import get_group_by_name, find_group_by_name


class Client:
    def __init__(self, grouper_base_url: str, username: str, password: str) -> None:
        self.client = httpx.Client(
            auth=httpx.BasicAuth(username=username, password=password),
            base_url=grouper_base_url,
            headers={"Content-type": 'text/x-json;charset=UTF-8'}
        )

    def get_group(
        self,
        group_name: str
    ) -> "Group":
        return get_group_by_name(group_name, self.client)

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
