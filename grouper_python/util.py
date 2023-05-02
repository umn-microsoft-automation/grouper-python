from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .objects.client import GrouperClient
    from .objects.subject import Subject
import httpx
from copy import deepcopy
from .objects.exceptions import GrouperAuthException, GrouperSuccessException
from .group import get_group_by_name


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
    if result.status_code == 401:
        raise GrouperAuthException(result.text)
    data: dict[str, Any] = result.json()
    result_type = list(data.keys())[0]
    if data[result_type]["resultMetadata"]["success"] != "T":
        raise GrouperSuccessException(data)
    return data


def resolve_subject(
    subject_body: dict[str, Any],
    client: GrouperClient,
    subject_attr_names: list[str],
    resolve_group: bool,
) -> Subject:
    from .objects.person import Person
    from .objects.subject import Subject

    if subject_body["sourceId"] == "g:gsa":
        if resolve_group:
            return get_group_by_name(subject_body["name"], client)
        else:
            return Subject.from_results(
                client=client,
                subject_body=subject_body,
                subject_attr_names=subject_attr_names,
            )
    else:
        return Person.from_results(
            client=client,
            person_body=subject_body,
            subject_attr_names=subject_attr_names,
        )
