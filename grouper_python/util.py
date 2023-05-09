"""grouper-python.util - utility functions for interacting with Grouper.

These are "helper" functions that most likely will not be called directly.
Instead, a Client class should be created, then from there use that Client's
methods to find and create objects, and use those objects' methods.
These helper functions are used by those objects, but can be called
directly if needed.
"""

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
    """Call the Grouper API.

    :param client: httpx Client object to use
    :type client: httpx.Client
    :param path: API url suffix to call
    :type path: str
    :param body: body to be sent with API call
    :type body: dict[str, Any]
    :param method: HTTP method, defaults to "POST"
    :type method: str, optional
    :param act_as_subject_id: Optional subject id to act as,
    cannot be specified if act_as_subject_identifer is specified,
    defaults to None
    :type act_as_subject_id: str | None, optional
    :param act_as_subject_identifier: Optional subject identifier to act as,
    cannot be specified if act_as_subject_id is specified
    defaults to None
    :type act_as_subject_identifier: str | None, optional
    :raises ValueError: Both act_as_subject_id and act_as_subject_identifier
    were specified.
    :raises GrouperAuthException: There is an issue authenticating to the Grouper API
    :raises GrouperSuccessException: The result was not "succesful"
    :return: the full payload returned from Grouper
    :rtype: dict[str, Any]
    """
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
    """Resolve a given subject.

    :param subject_body: The body of the subject to resolve
    :type subject_body: dict[str, Any]
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param subject_attr_names: subject attribute names for the given subject body
    :type subject_attr_names: list[str]
    :param resolve_group: Whether to resolve the subject to a Group object if it is
    a group. Resolving will require an additional API call.
    If True, the group will be resolved and returned as a Group.
    If False, the group will be returned as a Subject.
    :type resolve_group: bool
    :return: The final "resolved" Subject.
    :rtype: Subject
    """
    from .objects.person import Person
    from .objects.subject import Subject

    if subject_body["sourceId"] == "g:gsa":
        if resolve_group:
            return get_group_by_name(subject_body["name"], client)
        else:
            return Subject(
                client=client,
                subject_body=subject_body,
                subject_attr_names=subject_attr_names,
            )
    else:
        return Person(
            client=client,
            person_body=subject_body,
            subject_attr_names=subject_attr_names,
        )
