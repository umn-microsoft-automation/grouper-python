from __future__ import annotations
from typing import Any
import httpx
from copy import deepcopy
from .objects.exceptions import GrouperAuthException, GrouperSuccessException


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
