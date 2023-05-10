"""grouper-python.subject - functions to interact with subject objects.

These are "helper" functions that most likely will not be called directly.
Instead, a GrouperClient class should be created, then from there use that
GrouperClient's methods to find and create objects, and use those objects' methods.
These helper functions are used by those objects, but can be called
directly if needed.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .objects.group import Group
    from .objects.client import GrouperClient
    from .objects.subject import Subject
from .objects.exceptions import GrouperSubjectNotFoundException
from .util import resolve_subject


def get_groups_for_subject(
    subject_id: str,
    client: GrouperClient,
    stem: str | None = None,
    substems: bool = True,
    act_as_subject: Subject | None = None,
) -> list[Group]:
    """Get groups the given subject is a member of.

    :param subject_id: Subject id of subject to get groups
    :type subject_id: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param stem: Optional stem to limit the search to, defaults to None
    :type stem: str | None, optional
    :param substems: Whether to look recursively through substems
    of the given stem (True), or only one level in the given stem (False),
    defaults to True
    :type substems: bool, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :return: List of found groups, will be an empty list if no groups are found
    :rtype: list[Group]
    """
    from .objects.group import Group

    body: dict[str, Any] = {
        "WsRestGetMembershipsRequest": {
            "fieldName": "members",
            "wsSubjectLookups": [{"subjectId": subject_id}],
            "includeGroupDetail": "T",
        }
    }
    if stem:
        body["WsRestGetMembershipsRequest"]["wsStemLookup"] = {"stemName": stem}
        if substems:
            body["WsRestGetMembershipsRequest"]["stemScope"] = "ALL_IN_SUBTREE"
        else:
            body["WsRestGetMembershipsRequest"]["stemScope"] = "ONE_LEVEL"
    r = client._call_grouper(
        "/memberships",
        body,
        act_as_subject=act_as_subject,
    )
    if "wsGroups" in r["WsGetMembershipsResults"]:
        return [
            Group(client, grp)
            for grp in r["WsGetMembershipsResults"]["wsGroups"]
        ]
    else:
        return []


def get_subject_by_identifier(
    subject_identifier: str,
    client: GrouperClient,
    resolve_group: bool = True,
    attributes: list[str] = [],
    act_as_subject: Subject | None = None,
) -> Subject:
    """Get the subject with the given identifier.

    :param subject_identifier: Identifier of subject to get
    :type subject_identifier: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param resolve_group: Whether to resolve subject that is a group into a Group
    object, which will require an additional API for each found group,
    defaults to True
    :type resolve_group: bool, optional
    :param attributes: Additional attributes to return for the Subject,
    defaults to []
    :type attributes: list[str], optional
    :param act_as_subject:  Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises GrouperSubjectNotFoundException: A subject cannot be found
    with the given identifier
    :raises GrouperSuccessException: An otherwise unhandled issue with the result
    :return: The subject with the given name
    :rtype: Subject
    """
    attribute_set = set(attributes + [client.universal_identifier_attr, "name"])
    body = {
        "WsRestGetSubjectsRequest": {
            "wsSubjectLookups": [{"subjectIdentifier": subject_identifier}],
            "includeSubjectDetail": "T",
            "subjectAttributeNames": [*attribute_set],
        }
    }
    r = client._call_grouper("/subjects", body, act_as_subject=act_as_subject)
    subject = r["WsGetSubjectsResults"]["wsSubjects"][0]
    if subject["success"] == "F":
        raise GrouperSubjectNotFoundException(subject_identifier, r)
    return resolve_subject(
        subject_body=subject,
        client=client,
        subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
        resolve_group=resolve_group,
    )


def find_subjects(
    search_string: str,
    client: GrouperClient,
    resolve_groups: bool = True,
    attributes: list[str] = [],
    act_as_subject: Subject | None = None,
) -> list[Subject]:
    """Find subjects with the given search string.

    :param search_string: Free-form string tos earch for
    :type search_string: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param resolve_groups: Whether to resolve subjects that are groups into Group
    objects, which will require an additional API call per group, defaults to True
    :type resolve_groups: bool, optional
    :param attributes: Additional attributes to return for the Subject,
    defaults to []
    :type attributes: list[str], optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises GrouperSuccessException: An otherwise unhandled issue with the result
    :return: List of found Subjects, will be an empty list if no subjects are found
    :rtype: list[Subject]
    """
    attribute_set = set(attributes + [client.universal_identifier_attr, "name"])
    body = {
        "WsRestGetSubjectsRequest": {
            "searchString": search_string,
            "includeSubjectDetail": "T",
            "subjectAttributeNames": [*attribute_set],
        }
    }
    r = client._call_grouper("/subjects", body, act_as_subject=act_as_subject)
    if "wsSubjects" in r["WsGetSubjectsResults"]:
        subject_attr_names = r["WsGetSubjectsResults"]["subjectAttributeNames"]
        return [
            resolve_subject(
                subject_body=subject,
                client=client,
                subject_attr_names=subject_attr_names,
                resolve_group=resolve_groups,
            )
            for subject in r["WsGetSubjectsResults"]["wsSubjects"]
        ]
    else:
        return []
