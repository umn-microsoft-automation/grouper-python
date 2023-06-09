"""grouper_python.objects.attribute - Objects related to Grouper attributes."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .group import Group
    from .stem import Stem
    from .client import GrouperClient
from dataclasses import dataclass
from .base import GrouperEntity, GrouperBase


@dataclass(slots=True, eq=False)
class AttributeDefinition(GrouperEntity):
    """AttributeDefinition object representing a Grouper attribute definition.

    :param client: A GrouperClient object containing connection information
    :type client: GrouperClient
    :param attribute_def_body: Body of the attribute definition
    as returned by the Grouper API
    :type attribute_def_body: dict[str, str]
    """

    extension: str
    attributeDefType: str
    valueType: str
    assignToAttributeDef: str
    assignToStem: str
    assignToGroup: str
    assignToMember: str
    assignToEffectiveMembership: str
    assignToImmediateMembership: str
    assignToAttributeDefAssignment: str
    assignToStemAssignment: str
    assignToGroupAssignment: str
    assignToMemberAssignment: str
    assignToEffectiveMembershipAssignment: str
    assignToImmediateMembershipAssignment: str
    multiAssignable: str
    multiValued: str
    idIndex: str

    def __init__(
        self,
        client: GrouperClient,
        attribute_def_body: dict[str, str]
    ) -> None:
        """Construct an AttributeDefinition."""
        self.client = client
        self.description = attribute_def_body.get("description", "")
        self.id = attribute_def_body["uuid"]
        for key, value in attribute_def_body.items():
            if key not in ["description", "uuid"]:
                setattr(self, key, value)


@dataclass(slots=True, eq=False)
class AttributeDefinitionName(GrouperEntity):
    """AttributeDefinitionName object representing a Grouper attribute definition name.

    :param client: A GrouperClient object containing connection information
    :type client: GrouperClient
    :param attribute_def_name_body: Body of the attribute definition name
    as returned by the Grouper API
    :type attribute_def_name_body: dict[str, str]
    :param attribute_def: AttributeDefinition object associated with this
    attribute definition name
    :type attribute_def: AttributeDefinition
    """

    displayExtension: str
    extension: str
    displayName: str
    idIndex: str
    attribute_definition: AttributeDefinition

    def __init__(
        self,
        client: GrouperClient,
        attribute_def_name_body: dict[str, str],
        attribute_def: AttributeDefinition
    ) -> None:
        """Construct an AttributeDefinitionName."""
        self.client = client
        self.displayExtension = attribute_def_name_body["displayExtension"]
        self.extension = attribute_def_name_body["extension"]
        self.displayName = attribute_def_name_body["displayName"]
        self.idIndex = attribute_def_name_body["idIndex"]
        self.name = attribute_def_name_body["name"]
        self.description = attribute_def_name_body.get("description", "")
        self.id = attribute_def_name_body["uuid"]
        self.attribute_definition = attribute_def


@dataclass
class AttributeAssignmentValue:
    """Class representing an attribute assignment value."""

    id: str
    valueSystem: str


@dataclass(slots=True, eq=False)
class AttributeAssignment(GrouperBase):
    """AttributeAssignemtn object representing a Grouper attribute assignment.

    :param client: A GrouperClient object containing connection information
    :type client: GrouperClient
    :param assign_body: Body of the assignment as returned by the Grouper API
    :type assign_body: dict[str, Any]
    :param attribute_def: AttributeDefinition object associated with this assignment
    :type attribute_def: AttributeDefinition
    :param attribute_def_name: AttributeDefinitionName object
    associated with this assignment
    :type attribute_def_name: AttributeDefinitionName
    :param group: owner group of this assignment, defaults to None
    :type group: Group | None, optional
    :param stem: owner stem of this assignment, defaults to None
    :type stem: Stem | None, optional
    """

    attributeAssignDelegatable: str
    disallowed: str
    createdOn: str
    enabled: str
    attributeAssignType: str
    lastUpdated: str
    attributeAssignActionId: str
    attributeAssignActionName: str
    attributeAssignActionType: str
    owner: Group | Stem
    group: Group | None
    stem: Stem | None
    values: list[AttributeAssignmentValue]
    attribute_definition: AttributeDefinition
    attribute_definition_name: AttributeDefinitionName

    def __init__(
        self,
        client: GrouperClient,
        assign_body: dict[str, Any],
        attribute_def: AttributeDefinition,
        attribute_def_name: AttributeDefinitionName,
        *,
        group: Group | None = None,
        stem: Stem | None = None
    ) -> None:
        """Construct an AttributeAssignment."""
        self.client = client
        self.attributeAssignDelegatable = assign_body["attributeAssignDelegatable"]
        self.disallowed = assign_body["disallowed"]
        self.createdOn = assign_body["createdOn"]
        self.enabled = assign_body["enabled"]
        self.attributeAssignType = assign_body["attributeAssignType"]
        self.lastUpdated = assign_body["lastUpdated"]
        self.attributeAssignActionId = assign_body["attributeAssignActionId"]
        self.attributeAssignActionName = assign_body["attributeAssignActionName"]
        self.attributeAssignActionType = assign_body["attributeAssignActionType"]
        self.group = group
        self.stem = stem
        if group:
            self.owner = group
        if stem:
            self.owner = stem
        self.values = [
            AttributeAssignmentValue(val["id"], val["valueSystem"])
            for val in assign_body["wsAttributeAssignValues"]
        ] if "wsAttributeAssignValues" in assign_body else []
        self.attribute_definition = attribute_def
        self.attribute_definition_name = attribute_def_name
