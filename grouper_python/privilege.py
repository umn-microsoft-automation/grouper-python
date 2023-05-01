from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .objects.client import Client
    from .objects.subject import Subject
    from .objects.privilege import Privilege
from .objects.exceptions import (
    GrouperSuccessException,
    GrouperSubjectNotFoundException,
    GrouperGroupNotFoundException,
    GrouperStemNotFoundException,
)


def assign_privilege(
    target: str,
    target_type: str,
    privilege_name: str,
    entity_identifier: str,
    allowed: str,
    client: Client,
    act_as_subject: Subject | None = None,
) -> None:
    body = {
        "WsRestAssignGrouperPrivilegesLiteRequest": {
            "allowed": allowed,
            "privilegeName": privilege_name,
            "subjectIdentifier": entity_identifier,
        }
    }
    if target_type == "stem":
        body["WsRestAssignGrouperPrivilegesLiteRequest"]["stemName"] = target
        body["WsRestAssignGrouperPrivilegesLiteRequest"]["privilegeType"] = "naming"
    elif target_type == "group":
        body["WsRestAssignGrouperPrivilegesLiteRequest"]["groupName"] = target
        body["WsRestAssignGrouperPrivilegesLiteRequest"]["privilegeType"] = "access"
    else:
        raise ValueError(
            f"Target type must be either 'stem' or 'group', but got '{target_type}'."
        )
    client._call_grouper(
        "/grouperPrivileges",
        body,
        act_as_subject=act_as_subject,
    )


def get_privileges(
    client: Client,
    subject_id: str | None = None,
    subject_identifier: str | None = None,
    group_name: str | None = None,
    stem_name: str | None = None,
    privilege_name: str | None = None,
    privilege_type: str | None = None,
    attributes: list[str] = [],
    act_as_subject: Subject | None = None,
) -> list[Privilege]:
    from .objects.privilege import Privilege

    if subject_id and subject_identifier:
        raise ValueError("Only specify one of subject_id or subject_identifier.")
    if group_name and stem_name:
        raise ValueError("Only specify one of group_name or stem_name.")
    if not subject_id and not subject_identifier and not group_name and not stem_name:
        raise ValueError(
            "Must specify a valid target to retrieve privileges for."
            " Specify either a subject, a stem, a group,"
            " a subject and stem, or a subject and group."
        )
    request = {
        "includeSubjectDetail": "T",
        "includeGroupDetail": "T",
        "subjectAttributeNames": ",".join(attributes),
    }
    if subject_id:
        request["subjectId"] = subject_id
    elif subject_identifier:
        request["subjectIdentifier"] = subject_identifier
    if group_name:
        request["groupName"] = group_name
    elif stem_name:
        request["stemName"] = stem_name
    if privilege_name:
        request["privilegeName"] = privilege_name
    if privilege_type:
        request["privilegeType"] = privilege_type
    body = {"WsRestGetGrouperPrivilegesLiteRequest": request}
    try:
        r = client._call_grouper(
            "/grouperPrivileges",
            body,
            act_as_subject=act_as_subject,
        )
        result = r["WsGetGrouperPrivilegesLiteResult"]
        return [
            Privilege.from_results(client, priv, result["subjectAttributeNames"])
            for priv in result["privilegeResults"]
        ]
    except GrouperSuccessException as err:
        r = err.grouper_result
        r_code = r["WsGetGrouperPrivilegesLiteResult"]["resultMetadata"]["resultCode"]
        if r_code == "SUBJECT_NOT_FOUND":
            raise GrouperSubjectNotFoundException(
                subject_identifier=str(subject_identifier)
                if subject_identifier
                else str(subject_id),
                grouper_result=r,
            )
        elif r_code == "GROUP_NOT_FOUND":
            raise GrouperGroupNotFoundException(str(group_name), r)
        elif r_code == "STEM_NOT_FOUND":
            raise GrouperStemNotFoundException(str(stem_name), r)
        else:  # pragma: no cover
            # We don't know what went wrong,
            # so raise the original SuccessException
            raise err
