from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .group import Group
    from .stem import Stem
    from .subject import Subject
    from types import TracebackType
import httpx
from ..util import call_grouper
# from ..util import (
#     call_grouper,
#     # get_stem_by_name,
#     # get_subject_by_identifier,
#     # get_group_by_name,
#     # find_group_by_name,
# )
from ..group import get_group_by_name, find_group_by_name
from ..stem import get_stem_by_name
from ..subject import get_subject_by_identifier


class Client:
    def __init__(
        self,
        grouper_base_url: str,
        username: str,
        password: str,
        timeout: float = 30.0,
        universal_identifier_attr: str = "description",
    ) -> None:
        self.httpx_client = httpx.Client(
            auth=httpx.BasicAuth(username=username, password=password),
            base_url=grouper_base_url,
            headers={"Content-type": "text/x-json;charset=UTF-8"},
            timeout=timeout,
        )
        self.universal_identifier_attr = universal_identifier_attr

    def __enter__(self) -> Client:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        self.httpx_client.close()

    def get_group(
        self,
        group_name: str,
        act_as_subject: Subject | None = None,
    ) -> "Group":
        return get_group_by_name(
            group_name=group_name,
            client=self,
            act_as_subject=act_as_subject
        )

    def get_groups(
        self,
        group_name: str,
        stem: str | None = None,
        act_as_subject: Subject | None = None,
    ) -> list["Group"]:
        return find_group_by_name(
            group_name=group_name,
            client=self,
            stem=stem,
            act_as_subject=act_as_subject
        )

    def get_stem(self, stem_name: str) -> "Stem":
        return get_stem_by_name(stem_name, self)

    def get_subject(
        self,
        subject_identifier: str,
        resolve_group: bool = True,
        attributes: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> Subject:
        return get_subject_by_identifier(
            subject_identifier=subject_identifier,
            client=self,
            resolve_group=resolve_group,
            attributes=attributes,
            act_as_subject=act_as_subject
        )

    def _call_grouper(
        self,
        path: str,
        body: dict[str, Any],
        method: str = "POST",
        act_as_subject: Subject | None = None,
    ) -> dict[str, Any]:
        return call_grouper(
            client=self.httpx_client,
            path=path,
            body=body,
            method=method,
            act_as_subject_id=(act_as_subject.id if act_as_subject else None)
        )
