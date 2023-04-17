from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .group import Group
    from .stem import Stem
    from .subject import Subject
import httpx
from .stem import get_stem_by_name
from .subject import get_subject_by_identifier
from .group import get_group_by_name, find_group_by_name


class Client:
    def __init__(self, grouper_base_url: str, username: str, password: str) -> None:
        self.client = httpx.Client(
            auth=httpx.BasicAuth(username=username, password=password),
            base_url=grouper_base_url,
            headers={"Content-type": "text/x-json;charset=UTF-8"},
            timeout=30.0
        )

    def get_group(
        self,
        group_name: str,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> "Group":
        return get_group_by_name(
            group_name,
            self.client,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def get_groups(
        self,
        group_name: str,
        stem: str | None = None,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> list["Group"]:
        return find_group_by_name(
            group_name=group_name,
            client=self.client,
            stem=stem,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def get_stem(self, stem_name: str) -> "Stem":
        return get_stem_by_name(stem_name, self.client)

    def get_subject(
        self,
        subject_identifier: str,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> "Subject":
        return get_subject_by_identifier(
            subject_identifier,
            self.client,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
