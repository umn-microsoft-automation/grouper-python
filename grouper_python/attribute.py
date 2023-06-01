"""grouper-python.attribute - functions to interact with grouper attributess.

These are "helper" functions that normally will not be called directly.
However these are still in development, so do not return Python types,
and are not usable from any objects currently.
They can be used by calling directly.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    # from .objects.group import CreateGroup, Group
    from .objects.client import GrouperClient
    from .objects.subject import Subject
# from .objects.exceptions import (
#     GrouperGroupNotFoundException,
#     GrouperSuccessException,
#     GrouperStemNotFoundException,
#     GrouperPermissionDenied,
# )


def assign_attribute(
    attribute_assign_type: str,
    assign_operation: str,
    client: GrouperClient,
    # owner_id: str | None = None,
    attribute_assign_id: str | None = None,
    owner_name: str | None = None,
    attribute_def_name_name: str | None = None,
    value: None | str | int | float = None,
    assign_value_operation: str | None = None,
    act_as_subject: Subject | None = None,
) -> dict[str, Any]:
    """Assign an attribute.

    :param attribute_assign_type: _description_
    :type attribute_assign_type: str
    :param assign_operation: _description_
    :type assign_operation: str
    :param client: _description_
    :type client: GrouperClient
    :param attribute_assign_id: _description_, defaults to None
    :type attribute_assign_id: str | None, optional
    :param owner_name: _description_, defaults to None
    :type owner_name: str | None, optional
    :param attribute_def_name_name: _description_, defaults to None
    :type attribute_def_name_name: str | None, optional
    :param value: _description_, defaults to None
    :type value: None | str | int | float, optional
    :param assign_value_operation: _description_, defaults to None
    :type assign_value_operation: str | None, optional
    :param act_as_subject: _description_, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises ValueError: _description_
    :return: _description_
    :rtype: dict[str, Any]
    """
    request: dict[str, Any] = {
        # "WsRestAssignAttributesLiteRequest": {
        # "wsAttributeDefNameName": attribute_def_name_name,
        "attributeAssignType": attribute_assign_type,
        "attributeAssignOperation": assign_operation,
    }
    # }
    if attribute_assign_type == "group":
        if owner_name:
            request["wsOwnerGroupLookups"] = [{"groupName": owner_name}]
        else:
            request["wsOwnerGroupLookups"] = []
        # request["wsOwnerGroupName"] = owner_name
    # elif attribute_assign_type == "member":
    #     request["wsOwnerSubjectIdentifier"] = owner_name
    # elif attribute_assign_type == "stem":
    #     request["wsOwnerStemName"] = owner_name
    # elif attribute_assign_type == "attr_def":
    #     request["wsOwnerAttributeDefName"] = owner_name
    else:
        raise ValueError("Unknown or unsupported attributeAssignType given")
    if attribute_assign_id:
        request["wsAttributeAssignLookups"] = [{"uuid": attribute_assign_id}]
    if attribute_def_name_name:
        request["wsAttributeDefNameLookups"] = [{"name": attribute_def_name_name}]

    if value and assign_value_operation:
        request["values"] = [{"valueSystem": value}]
        request["attributeAssignValueOperation"] = assign_value_operation

    body = {"WsRestAssignAttributesRequest": request}

    r = client._call_grouper(
        "/attributeAssignments", body, act_as_subject=act_as_subject
    )

    return r


def get_attribute_assignments(
    attribute_assign_type: str,
    client: GrouperClient,
    attribute_def_name_name: str | None = None,
    attribute_def_name: str | None = None,
    owner_name: str | None = None,
    include_assignments_on_assignments: str = "F",
    # value: None | str | int | float = None,
    # assign_value_operation: str | None = None,
    act_as_subject: Subject | None = None,
) -> dict[str, Any]:
    """Get attribute assignments.

    :param attribute_assign_type: _description_
    :type attribute_assign_type: str
    :param client: _description_
    :type client: GrouperClient
    :param attribute_def_name_name: _description_, defaults to None
    :type attribute_def_name_name: str | None, optional
    :param attribute_def_name: _description_, defaults to None
    :type attribute_def_name: str | None, optional
    :param owner_name: _description_, defaults to None
    :type owner_name: str | None, optional
    :param include_assignments_on_assignments: _description_, defaults to "F"
    :type include_assignments_on_assignments: str, optional
    :param act_as_subject: _description_, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises ValueError: _description_
    :return: _description_
    :rtype: dict[str, Any]
    """
    request = {
        "attributeAssignType": attribute_assign_type,
        "includeAssignmentsOnAssignments": include_assignments_on_assignments,
    }
    if owner_name:
        if attribute_assign_type == "group":
            request["wsOwnerGroupName"] = owner_name
        elif attribute_assign_type == "member":
            request["wsOwnerSubjectIdentifier"] = owner_name
        elif attribute_assign_type == "stem":
            request["wsOwnerStemName"] = owner_name
        elif attribute_assign_type == "attr_def":
            request["wsOwnerAttributeDefName"] = owner_name
        else:
            raise ValueError("Unknown or unsupported attributeAssignType given")
    if attribute_def_name_name:
        request["wsAttributeDefNameName"] = attribute_def_name_name
    if attribute_def_name:
        request["wsAttributeDefName"] = attribute_def_name

    body = {"WsRestGetAttributeAssignmentsLiteRequest": request}

    r = client._call_grouper(
        "/attributeAssignments", body, act_as_subject=act_as_subject
    )

    return r
