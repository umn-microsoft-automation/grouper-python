"""grouper-python.attribute - functions to interact with grouper attributess.

These are "helper" functions that normally will not be called directly.
However these are still in development,
and are not usable from any objects currently.
They can be used by calling directly.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any, overload, Literal

if TYPE_CHECKING:  # pragma: no cover
    from .objects.client import GrouperClient
    from .objects.subject import Subject
    from .objects.attribute import (
        AttributeDefinition,
        AttributeDefinitionName,
        AttributeAssignment,
    )


@overload
def assign_attribute(
    attribute_assign_type: str,
    assign_operation: str,
    client: GrouperClient,
    attribute_assign_id: str | None = None,
    owner_name: str | None = None,
    attribute_def_name_name: str | None = None,
    value: None | str | int | float = None,
    assign_value_operation: str | None = None,
    *,
    raw: Literal[False] = False,
    act_as_subject: Subject | None = None,
) -> list[AttributeAssignment]:  # pragma: no cover
    ...


@overload
def assign_attribute(
    attribute_assign_type: str,
    assign_operation: str,
    client: GrouperClient,
    attribute_assign_id: str | None = None,
    owner_name: str | None = None,
    attribute_def_name_name: str | None = None,
    value: None | str | int | float = None,
    assign_value_operation: str | None = None,
    *,
    raw: Literal[True],
    act_as_subject: Subject | None = None,
) -> dict[str, Any]:  # pragma: no cover
    ...


def assign_attribute(
    attribute_assign_type: str,
    assign_operation: str,
    client: GrouperClient,
    attribute_assign_id: str | None = None,
    owner_name: str | None = None,
    attribute_def_name_name: str | None = None,
    value: None | str | int | float = None,
    assign_value_operation: str | None = None,
    *,
    raw: bool = False,
    act_as_subject: Subject | None = None,
) -> list[AttributeAssignment] | dict[str, Any]:
    """Assign an attribute.

    :param attribute_assign_type: Type of attribute assignment,
    currently only "group" is supported
    :type attribute_assign_type: str
    :param assign_operation: Assignment operation, one of
    "assign_attr", "add_attr", "remove_attr", "replace_attrs"
    :type assign_operation: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param attribute_assign_id: Existing assignment id, if modifying
    an existing assignment, defaults to None
    :type attribute_assign_id: str | None, optional
    :param owner_name: Name of owner to assign attribute to,
    defaults to None
    :type owner_name: str | None, optional
    :param attribute_def_name_name: Attribute definition name name to assign,
    defaults to None
    :type attribute_def_name_name: str | None, optional
    :param value: Value to assign, also requires assign_value_operation,
    defaults to None
    :type value: None | str | int | float, optional
    :param assign_value_operation: Value assignment operation, one of
    "assign_value", "add_value", "remove_value", "replace_values",
    requires value to be specified as well, defaults to None
    :type assign_value_operation: str | None, optional
    :param raw: Whether to return a raw dictionary of results instead
    of Python objects, defaults to False
    :type raw: bool, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises ValueError: An unknown or unsupported attribute_assign_type is given
    :return: A list of modified AttributeAssignments or the raw dictionary result
    from Grouper, depending on the value of raw
    :rtype: list[AttributeAssignment] | dict[str, Any]
    """
    from .objects.attribute import (
        AttributeDefinition,
        AttributeDefinitionName,
        AttributeAssignment,
    )
    from .objects.group import Group
    from .objects.stem import Stem

    request: dict[str, Any] = {
        "attributeAssignType": attribute_assign_type,
        "attributeAssignOperation": assign_operation,
    }
    if attribute_assign_type == "group":
        if owner_name:
            request["wsOwnerGroupLookups"] = [{"groupName": owner_name}]
        else:
            request["wsOwnerGroupLookups"] = []
    elif attribute_assign_type == "stem":
        if owner_name:
            request["wsOwnerStemLookups"] = [{"stemName": owner_name}]
        else:
            request["wsOwnerStemLookups"] = []
    elif attribute_assign_type == "member":  # pragma: no cover
        if owner_name:
            request["wsOwnerSubjectLookups"] = [{"identifier": owner_name}]
        else:
            request["wsOwnerSubjectLookups"] = []
    elif attribute_assign_type == "attr_def":  # pragma: no cover
        if owner_name:
            request["wsOwnerAttributeLookups"] = [{"name": owner_name}]
        else:
            request["wsOwnerAttributeLookups"] = []
    else:  # pragma: no cover
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
    if raw:  # pragma: no cover
        return r

    results = r["WsAssignAttributesResults"]

    ws_attribute_defs = results["wsAttributeDefs"]
    ws_attribute_def_names = results["wsAttributeDefNames"]
    _attribute_defs = {
        ws_attr_def["uuid"]: AttributeDefinition(client, ws_attr_def)
        for ws_attr_def in ws_attribute_defs
    }
    _attribute_def_names = {
        ws_attr_def_name["uuid"]: AttributeDefinitionName(
            client,
            ws_attr_def_name,
            _attribute_defs[ws_attr_def_name["attributeDefId"]],
        )
        for ws_attr_def_name in ws_attribute_def_names
    }

    r_list: list[AttributeAssignment] = []

    if attribute_assign_type == "group":
        groups = {group["uuid"]: Group(client, group) for group in results["wsGroups"]}
        for assign_result in results["wsAttributeAssignResults"]:
            for assg in assign_result["wsAttributeAssigns"]:
                r_list.append(
                    AttributeAssignment(
                        client,
                        assg,
                        _attribute_defs[assg["attributeDefId"]],
                        _attribute_def_names[assg["attributeDefNameId"]],
                        group=groups[assg["ownerGroupId"]],
                    )
                )
    elif attribute_assign_type == "stem":
        stems = {stem["uuid"]: Stem(client, stem) for stem in results["wsStems"]}
        for assign_result in results["wsAttributeAssignResults"]:
            for assg in assign_result["wsAttributeAssigns"]:
                r_list.append(
                    AttributeAssignment(
                        client,
                        assg,
                        _attribute_defs[assg["attributeDefId"]],
                        _attribute_def_names[assg["attributeDefNameId"]],
                        stem=stems[assg["ownerStemId"]],
                    )
                )
    else:  # pragma: no cover
        raise ValueError("Unknown or unsupported attributeAssignType given, use raw")

    return r_list


@overload
def get_attribute_assignments(
    attribute_assign_type: str,
    client: GrouperClient,
    attribute_def_name_names: list[str] = [],
    attribute_def_names: list[str] = [],
    owner_names: list[str] = [],
    include_assignments_on_assignments: str = "F",
    *,
    raw: Literal[False] = False,
    act_as_subject: Subject | None = None,
) -> list[AttributeAssignment]:  # pragma: no cover
    ...


@overload
def get_attribute_assignments(
    attribute_assign_type: str,
    client: GrouperClient,
    attribute_def_name_names: list[str] = [],
    attribute_def_names: list[str] = [],
    owner_names: list[str] = [],
    include_assignments_on_assignments: str = "F",
    *,
    raw: Literal[True],
    act_as_subject: Subject | None = None,
) -> dict[str, Any]:  # pragma: no cover
    ...


def get_attribute_assignments(
    attribute_assign_type: str,
    client: GrouperClient,
    attribute_def_name_names: list[str] = [],
    attribute_def_names: list[str] = [],
    owner_names: list[str] = [],
    include_assignments_on_assignments: str = "F",
    *,
    raw: bool = False,
    act_as_subject: Subject | None = None,
) -> list[AttributeAssignment] | dict[str, Any]:
    """Get attribute assignments.

    :param attribute_assign_type: Type of attribute assignment,
    must be a direct assignment type, one of
    "group", "member", "stem", "any_mem", "imm_mem", "attr_def"
    :type attribute_assign_type: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param attribute_def_name_names: List of names of attribute definition names
    to retrieve assignments for, defaults to []
    :type attribute_def_name_names: list[str], optional
    :param attribute_def_names: List of names of attribute defitions
    to retrieve assignments for, defaults to []
    :type attribute_def_names: list[str], optional
    :param owner_names: List of owners to retrieve assignments for,
    if specified, only group, member, stem, or attr_def
    are allowed for attribute_assign_type, defaults to []
    :type owner_names: list[str], optional
    :param include_assignments_on_assignments: Specify "T" to get
    assignments on assignments, defaults to "F"
    :type include_assignments_on_assignments: str, optional
    :param raw: Whether to return a raw dictionary of results instead
    of Python objects, defaults to False
    :type raw: bool, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :raises ValueError: An unknown or unsupported attribute_assign_type is given
    :raises ValueError: The given attribute_assign_type is not supported as a Python
    object, specify raw instead
    :return:a list of AttributeAssignments or the raw dictionary result
    from Grouper, depending on the value of raw
    :rtype: list[AttributeAssignment] | dict[str, Any]
    """
    from .objects.attribute import (
        AttributeDefinition,
        AttributeDefinitionName,
        AttributeAssignment,
    )
    from .objects.group import Group
    from .objects.stem import Stem

    request: dict[str, Any] = {
        "attributeAssignType": attribute_assign_type,
        "includeAssignmentsOnAssignments": include_assignments_on_assignments,
    }

    if attribute_assign_type == "group":
        request["wsOwnerGroupLookups"] = [{"groupName": name} for name in owner_names]
    elif attribute_assign_type == "stem":
        request["wsOwnerStemLookups"] = [{"stemName": name} for name in owner_names]
    elif attribute_assign_type == "member":  # pragma: no cover
        request["wsOwnerSubjectLookups"] = [
            {"identifier": name} for name in owner_names
        ]
    elif attribute_assign_type == "attr_def":  # pragma: no cover
        request["wsOwnerAttributeLookups"] = [{"name": name} for name in owner_names]
    else:  # pragma: no cover
        raise ValueError("Unknown or unsupported attributeAssignType given")

    request["wsAttributeDefNameLookups"] = [
        {"name": name} for name in attribute_def_name_names
    ]
    request["wsAttributeDefLookups"] = [{"name": name} for name in attribute_def_names]

    body = {"WsRestGetAttributeAssignmentsRequest": request}

    r = client._call_grouper(
        "/attributeAssignments", body, act_as_subject=act_as_subject
    )
    if raw:  # pragma: no cover
        return r

    results = r["WsGetAttributeAssignmentsResults"]

    if "wsAttributeAssigns" not in results:
        return []

    ws_attribute_defs = results["wsAttributeDefs"]
    ws_attribute_def_names = results["wsAttributeDefNames"]
    _attribute_defs = {
        ws_attr_def["uuid"]: AttributeDefinition(client, ws_attr_def)
        for ws_attr_def in ws_attribute_defs
    }
    _attribute_def_names = {
        ws_attr_def_name["uuid"]: AttributeDefinitionName(
            client,
            ws_attr_def_name,
            _attribute_defs[ws_attr_def_name["attributeDefId"]],
        )
        for ws_attr_def_name in ws_attribute_def_names
    }

    if attribute_assign_type == "group":
        groups = {group["uuid"]: Group(client, group) for group in results["wsGroups"]}
        return [
            AttributeAssignment(
                client,
                assg,
                _attribute_defs[assg["attributeDefId"]],
                _attribute_def_names[assg["attributeDefNameId"]],
                group=groups[assg["ownerGroupId"]],
            )
            for assg in results["wsAttributeAssigns"]
        ]
    elif attribute_assign_type == "stem":
        stems = {stem["uuid"]: Stem(client, stem) for stem in results["wsStems"]}
        return [
            AttributeAssignment(
                client,
                assg,
                _attribute_defs[assg["attributeDefId"]],
                _attribute_def_names[assg["attributeDefNameId"]],
                stem=stems[assg["ownerStemId"]],
            )
            for assg in results["wsAttributeAssigns"]
        ]
    else:  # pragma: no cover
        raise ValueError("Unknown or unsupported attributeAssignType given, use raw")


@overload
def get_attribute_definitions(
    attribute_def_name: str,
    client: GrouperClient,
    scope: str | None = None,
    split_scope: str = "F",
    parent_stem_id: str | None = None,
    stem_scope: str | None = None,
    *,
    raw: Literal[False] = False,
    act_as_subject: Subject | None = None,
) -> list[AttributeDefinition]:  # pragma: no cover
    ...


@overload
def get_attribute_definitions(
    attribute_def_name: str,
    client: GrouperClient,
    scope: str | None = None,
    split_scope: str = "F",
    parent_stem_id: str | None = None,
    stem_scope: str | None = None,
    *,
    raw: Literal[True],
    act_as_subject: Subject | None = None,
) -> dict[str, Any]:  # pragma: no cover
    ...


def get_attribute_definitions(
    attribute_def_name: str,
    client: GrouperClient,
    scope: str | None = None,
    split_scope: str = "F",
    parent_stem_id: str | None = None,
    stem_scope: str | None = None,
    *,
    raw: bool = False,
    act_as_subject: Subject | None = None,
) -> list[AttributeDefinition] | dict[str, Any]:
    """Get attribute definitions.

    Note: it appears that if the given attribute_def_name cannot
    be found exactly, the endpoint will return all definitions that
    match the remaining criteria.

    :param attribute_def_name: Name of attribute definition to get
    :type attribute_def_name: str
    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param scope: Search string with % as wildcards will search name,
    display name, description, defaults to None
    :type scope: str | None, optional
    :param split_scope: "T" or "F", if T will split the scope by whitespace,
    and find attribute defs with each token, defaults to "F"
    :type split_scope: str, optional
    :param parent_stem_id: ID of parent stem to limit search for,
    if specified stem_scope is also required, defaults to None
    :type parent_stem_id: str | None, optional
    :param stem_scope: Scope in stem to search for,
    if specified must be one of "ONE_LEVEL" or "ALL_IN_SUBTREE",
    and parent_stem_id must also be specified, defaults to None
    :type stem_scope: str | None, optional
    :param raw: Whether to return a raw dictionary of results instead
    of Python objects, defaults to False
    :type raw: bool, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :return: a list of AttributeDefinitions or the raw dictionary result
    from Grouper, depending on the value of raw
    :rtype: list[AttributeDefinition] | dict[str, Any]
    """
    from .objects.attribute import AttributeDefinition

    body = {
        "WsRestFindAttributeDefsLiteRequest": {
            "nameOfAttributeDef": attribute_def_name,
        }
    }
    if scope:
        body["WsRestFindAttributeDefsLiteRequest"]["scope"] = scope
        body["WsRestFindAttributeDefsLiteRequest"]["splitScope"] = split_scope

    if parent_stem_id and stem_scope:
        body["WsRestFindAttributeDefsLiteRequest"]["parentStemId"] = parent_stem_id
        body["WsRestFindAttributeDefsLiteRequest"]["stemScope"] = stem_scope

    r = client._call_grouper("/attributeDefs", body, act_as_subject=act_as_subject)
    if raw:
        return r
    results = r["WsFindAttributeDefsResults"]

    if "attributeDefResults" in results:
        return [
            AttributeDefinition(client, attribute_def_body)
            for attribute_def_body in results["attributeDefResults"]
        ]
    else:
        return []


@overload
def get_attribute_definition_names(
    client: GrouperClient,
    attribute_def_name_name: str | None = None,
    name_of_attribute_def: str | None = None,
    scope: str | None = None,
    *,
    raw: Literal[False] = False,
    act_as_subject: Subject | None = None,
) -> list[AttributeDefinitionName]:  # pragma: no cover
    ...


@overload
def get_attribute_definition_names(
    client: GrouperClient,
    attribute_def_name_name: str | None = None,
    name_of_attribute_def: str | None = None,
    scope: str | None = None,
    *,
    raw: Literal[True],
    act_as_subject: Subject | None = None,
) -> dict[str, Any]:  # pragma: no cover
    ...


def get_attribute_definition_names(
    client: GrouperClient,
    attribute_def_name_name: str | None = None,
    name_of_attribute_def: str | None = None,
    scope: str | None = None,
    *,
    raw: bool = False,
    act_as_subject: Subject | None = None,
) -> list[AttributeDefinitionName] | dict[str, Any]:
    """Get Attribute Definition Names.

    :param client: The GrouperClient to use
    :type client: GrouperClient
    :param attribute_def_name_name: The name of the attribute definition name
    to retrieve, defaults to None
    :type attribute_def_name_name: str | None, optional
    :param name_of_attribute_def: The name of the attribute definition to
    retrieve attribute definition names for, defaults to None
    :type name_of_attribute_def: str | None, optional
    :param scope: Search string with % as wildcards,
    will search name, display name, description, defaults to None
    :type scope: str | None, optional
    :param raw: Whether to return a raw dictionary of results instead
    of Python objects, defaults to False
    :type raw: bool, optional
    :param act_as_subject: Optional subject to act as, defaults to None
    :type act_as_subject: Subject | None, optional
    :return: a list of AttributeDefinitionNames or the raw dictionary result
    from Grouper, depending on the value of raw
    :rtype: list[AttributeDefinitionName] | dict[str, Any]
    """
    from .objects.attribute import AttributeDefinitionName, AttributeDefinition

    request: dict[str, str] = {}
    if attribute_def_name_name:
        request["attributeDefNameName"] = attribute_def_name_name
    if name_of_attribute_def:
        request["nameOfAttributeDef"] = name_of_attribute_def
    if scope:
        request["scope"] = scope
    body = {"WsRestFindAttributeDefNamesLiteRequest": request}

    r = client._call_grouper("/attributeDefNames", body, act_as_subject=act_as_subject)
    if raw:
        return r
    results = r["WsFindAttributeDefNamesResults"]

    if "attributeDefNameResults" not in results:
        return []

    ws_attribute_defs = results.get("attributeDefs", [])
    ws_attribute_def_names = results["attributeDefNameResults"]

    attribute_defs = {
        ws_attr_def["uuid"]: AttributeDefinition(client, ws_attr_def)
        for ws_attr_def in ws_attribute_defs
    }

    return [
        AttributeDefinitionName(
            client, attr_name, attribute_defs[attr_name["attributeDefId"]]
        )
        for attr_name in ws_attribute_def_names
    ]
