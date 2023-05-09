"""grouper-python.privilege - functions to interact with grouper privileges.

These are "helper" functions that most likely will not be called directly.
Instead, a Client class should be created, then from there use that Client's
methods to find and create objects, and use those objects' methods.
These helper functions are used by those objects, but can be called
directly if needed.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .objects.client import GrouperClient
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
    client: GrouperClient,
    act_as_subject: Subject | None = None,
) -> None:
    """Assign (or remove) a permission.

    :param target: Identifier of the target of the permission
    :type target: str
    :param target_type: Type of target, either "stem" or "group"
    :type target_type: str
    :param privilege_name: Name of the privilege to assign
    :type privilege_name: str
    :param entity_identifier: Identifier of the entity to receive the permission
    :type entity_identifier: str
    :param allowed: "T" to add the permission, "F" to remove it
    :type allowed: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises ValueError: An unknown/unsupported target_type is specified
    :raises GrouperSuccessException: An otherwise unhandled issue with the result
    """
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
    client: GrouperClient,
    subject_id: str | None = None,
    subject_identifier: str | None = None,
    group_name: str | None = None,
    stem_name: str | None = None,
    privilege_name: str | None = None,
    privilege_type: str | None = None,
    attributes: list[str] = [],
    act_as_subject: Subject | None = None,
) -> list[Privilege]:
    """Get privileges.

    Supports the following scenarios:
    Get all the permissions for a subject
    Get all permissions on a given group or stem
    Get all permissions for a subject on a given group or stem

    Privileges can additionally be filtered by name or type.
    If specifing a group or stem and a privilege type,
    the privilege type should align (eg naming for stem, access for group)
    or the Grouper API will return an error.

    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param subject_id: Subject ID of entity to get permissions for,
    cannot be specified if subject_identifier is specified, defaults to None
    :type subject_id: str | None, optional
    :param subject_identifier: Subject Identifier of entity to get permissions for,
    cannot be specified if subject_id is specified, defaults to None
    :type subject_identifier: str | None, optional
    :param group_name: Group name to get privileges for (possibly limited by subject),
    cannot be specified if stem_name is specified, defaults to None
    :type group_name: str | None, optional
    :param stem_name: Stem name to get privileges for (possibly limited by subject),
    cannot be specified if group_name is specified, defaults to None
    :type stem_name: str | None, optional
    :param privilege_name: Name of privilege to get, defaults to None
    :type privilege_name: str | None, optional
    :param privilege_type: Type of privilege to get, defaults to None
    :type privilege_type: str | None, optional
    :param attributes: Additional attributes to retrieve for the Subjects,
    defaults to []
    :type attributes: list[str], optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises ValueError: An invalid combination of parameters was given
    :raises GrouperSubjectNotFoundException: A subject cannot be found
    with the given identifier or id
    :raises GrouperGroupNotFoundException: A group with the given name cannot be found
    :raises GrouperStemNotFoundException: A stem with the given name cannot be found
    :raises GrouperSuccessException: An otherwise unhandled issue with the result
    :return: A list of retreived privileges satisfying the given constraints
    :rtype: list[Privilege]
    """
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
            Privilege(client, priv, result["subjectAttributeNames"])
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
