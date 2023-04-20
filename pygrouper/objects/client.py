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
        universal_id_attr: str = "description",
    ) -> None:
        self.httpx_client = httpx.Client(
            auth=httpx.BasicAuth(username=username, password=password),
            base_url=grouper_base_url,
            headers={"Content-type": "text/x-json;charset=UTF-8"},
            timeout=timeout,
        )
        self.universal_id_attr = universal_id_attr

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
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> "Group":
        return get_group_by_name(
            group_name=group_name,
            client=self,
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
            client=self,
            stem=stem,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def get_stem(self, stem_name: str) -> "Stem":
        return get_stem_by_name(stem_name, self)

    def get_subject(
        self,
        subject_identifier: str,
        resolve_group: bool = True,
        universal_id_attr: str | None = None,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> "Subject":
        return get_subject_by_identifier(
            subject_identifier=subject_identifier,
            client=self,
            resolve_group=resolve_group,
            universal_id_attr=(
                universal_id_attr if universal_id_attr else self.universal_id_attr
            ),
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )

    def _call_grouper(
        self,
        path: str,
        body: dict[str, Any],
        method: str = "POST",
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> dict[str, Any]:
        return call_grouper(
            client=self.httpx_client,
            path=path,
            body=body,
            method=method,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier,
        )
