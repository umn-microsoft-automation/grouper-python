from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .objects.group import Group
    from .objects.client import Client
    from .objects.subject import Subject
from .objects.exceptions import GrouperSubjectNotFoundException
from .group import get_group_by_name


def get_groups_for_subject(
    subject_id: str,
    client: Client,
    stem: str | None = None,
    substems: bool = True,
    act_as_subject: Subject | None = None,
) -> list[Group]:
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
            Group.from_results(client, grp)
            for grp in r["WsGetMembershipsResults"]["wsGroups"]
        ]
    else:
        return []


def get_subject_by_identifier(
    subject_identifier: str,
    client: Client,
    resolve_group: bool = True,
    attributes: list[str] = [],
    act_as_subject: Subject | None = None,
) -> Subject:
    from .objects.person import Person
    from .objects.subject import Subject

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
    if subject["sourceId"] == "g:gsa":
        if resolve_group:
            return get_group_by_name(subject["name"], client)
        else:
            return Subject.from_results(
                client=client,
                subject_body=subject,
                subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
            )
    else:
        return Person.from_results(
            client=client,
            person_body=subject,
            subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
        )


def find_subject(
    search_string: str,
    client: Client,
    resolve_group: bool = True,
    attributes: list[str] = [],
    act_as_subject: Subject | None = None,
) -> list[Subject]:
    from .objects.person import Person
    from .objects.subject import Subject

    attribute_set = set(attributes + [client.universal_identifier_attr, "name"])
    body = {
        "WsRestGetSubjectsRequest": {
            "searchString": search_string,
            "includeSubjectDetail": "T",
            "subjectAttributeNames": [*attribute_set],
        }
    }
    r = client._call_grouper("/subjects", body, act_as_subject=act_as_subject)
    r_list: list[Subject] = []
    if "wsSubjects" in r["WsGetSubjectsResults"]:
        subject_attr_names = r["WsGetSubjectsResults"]["subjectAttributeNames"]
        for subject in r["WsGetSubjectsResults"]["wsSubjects"]:
            if subject["sourceId"] == "g:gsa":
                if resolve_group:
                    r_list.append(get_group_by_name(subject["name"], client))
                else:
                    r_list.append(
                        Subject.from_results(
                            client=client,
                            subject_body=subject,
                            subject_attr_names=subject_attr_names,
                        )
                    )
            else:
                r_list.append(
                    Person.from_results(
                        client=client,
                        person_body=subject,
                        subject_attr_names=subject_attr_names,
                    )
                )
    return r_list
