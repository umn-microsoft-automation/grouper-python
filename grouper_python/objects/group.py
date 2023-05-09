"""grouper_python.subject - Class definition for Subject."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .membership import Membership, HasMember
    from .client import GrouperClient
    from .privilege import Privilege
from .subject import Subject
from dataclasses import dataclass
from ..membership import (
    get_members_for_groups,
    get_memberships_for_groups,
    add_members_to_group,
    delete_members_from_group,
    has_members,
)
from ..privilege import assign_privilege, get_privileges
from ..group import delete_groups


@dataclass(slots=True, eq=False)
class Group(Subject):
    """Group object representing a Grouper group.

    :param client: A GrouperClient object containing connection information
    :type client: GrouperClient
    :param group_body: Body of the group as returned by the Grouper API
    :type group_body: dict[str, Any]
    """

    extension: str
    displayName: str
    uuid: str
    enabled: str
    displayExtension: str
    typeOfGroup: str
    idIndex: str
    detail: dict[str, Any] | None

    def __init__(
        self,
        client: GrouperClient,
        group_body: dict[str, Any],
    ) -> None:
        """Construct a Group."""
        self.id = group_body["uuid"]
        self.description = group_body.get("description", "")
        self.universal_identifier = group_body["name"]
        self.sourceId = "g:gsa"
        self.name = group_body["name"]
        self.extension = group_body["extension"]
        self.displayName = group_body["displayName"]
        self.uuid = group_body["uuid"]
        self.enabled = group_body["enabled"]
        self.displayExtension = group_body["displayExtension"]
        self.typeOfGroup = group_body["typeOfGroup"]
        self.idIndex = group_body["idIndex"]
        self.detail = group_body.get("detail")
        self.client = client

    def get_members(
        self,
        attributes: list[str] = [],
        member_filter: str = "all",
        resolve_groups: bool = True,
        act_as_subject: Subject | None = None,
    ) -> list[Subject]:
        """Get members for this Group.

        :param attributes: Additional attributes to retrieve for the Subjects,
        defaults to []
        :type attributes: list[str], optional
        :param member_filter: Type of mebership to return (all, immediate, effective),
        defaults to "all"
        :type member_filter: str, optional
        :param resolve_groups: Whether to resolve subjects that are groups into Group
        objects, which will require an additional API call per group, defaults to True
        :type resolve_groups: bool, optional
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :return: List of members of this group
        :rtype: list[Subject]
        """
        members = get_members_for_groups(
            group_names=[self.name],
            client=self.client,
            attributes=attributes,
            member_filter=member_filter,
            resolve_groups=resolve_groups,
            act_as_subject=act_as_subject,
        )
        return members[self]

    def get_memberships(
        self,
        attributes: list[str] = [],
        member_filter: str = "all",
        resolve_groups: bool = True,
        act_as_subject: Subject | None = None,
    ) -> list[Membership]:
        """Get memberships for this group.

        Note that a "membership" includes more detail than a "member".

        :param attributes: Additional attributes to retrieve for the Subjects,
        defaults to []
        :type attributes: list[str], optional
        :param member_filter: Type of mebership to return (all, immediate, effective),
        defaults to "all"
        :type member_filter: str, optional
        :param resolve_groups: Whether to resolve subjects that are groups into Group
        objects, which will require an additional API call per group, defaults to True
        :type resolve_groups: bool, optional
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :return: List of memberships for this group
        :rtype: list[Membership]
        """
        memberships = get_memberships_for_groups(
            group_names=[self.name],
            client=self.client,
            attributes=attributes,
            member_filter=member_filter,
            resolve_groups=resolve_groups,
            act_as_subject=act_as_subject,
        )
        return memberships[self] if memberships else []

    def create_privilege_on_this(
        self,
        entity_identifier: str,
        privilege_name: str,
        act_as_subject: Subject | None = None,
    ) -> None:
        """Create a privilege on this Group.

        :param entity_identifier: Identifier of the entity to receive the permission
        :type entity_identifier: str
        :param privilege_name: Name of the privilege to assign
        :type privilege_name: str
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        """
        assign_privilege(
            target=self.name,
            target_type="group",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="T",
            client=self.client,
            act_as_subject=act_as_subject,
        )

    def delete_privilege_on_this(
        self,
        entity_identifier: str,
        privilege_name: str,
        act_as_subject: Subject | None = None,
    ) -> None:
        """Delete a privilege on this Group.

        :param entity_identifier: Identifier of the entity to remove permission for
        :type entity_identifier: str
        :param privilege_name: Name of the privilege to delete
        :type privilege_name: str
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        """
        assign_privilege(
            target=self.name,
            target_type="group",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="F",
            client=self.client,
            act_as_subject=act_as_subject,
        )

    def get_privilege_on_this(
        self,
        subject_id: str | None = None,
        subject_identifier: str | None = None,
        privilege_name: str | None = None,
        attributes: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> list[Privilege]:
        """Get privileges on this group

        :param subject_id: Subject Id to limit retreived permissions to,
        cannot be specified if subject_identifer is specified, defaults to None
        :type subject_id: str | None, optional
        :param subject_identifier: Subject Identifer to limit retreived permissions to,
        cannot be specified if subject_id is specified, defaults to None
        :type subject_identifier: str | None, optional
        :param privilege_name: Name of privilege to get, defaults to None
        :type privilege_name: str | None, optional
        :param attributes: Additional attributes to retrieve for the Subjects,
        defaults to []
        :type attributes: list[str], optional
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :return: List of retreived privileges on this group
        satisfying the given constraints
        :rtype: list[Privilege]
        """
        return get_privileges(
            client=self.client,
            subject_id=subject_id,
            subject_identifier=subject_identifier,
            group_name=self.name,
            privilege_name=privilege_name,
            attributes=attributes,
            act_as_subject=act_as_subject,
        )

    def add_members(
        self,
        subject_identifiers: list[str] = [],
        subject_ids: list[str] = [],
        replace_all_existing: str = "F",
        act_as_subject: Subject | None = None,
    ) -> None:
        add_members_to_group(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
            replace_all_existing=replace_all_existing,
            act_as_subject=act_as_subject,
        )

    def delete_members(
        self,
        subject_identifiers: list[str] = [],
        subject_ids: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> None:
        delete_members_from_group(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
            act_as_subject=act_as_subject,
        )

    def has_members(
        self,
        subject_identifiers: list[str] = [],
        subject_ids: list[str] = [],
        member_filter: str = "all",
        act_as_subject: Subject | None = None,
    ) -> dict[str, HasMember]:
        return has_members(
            group_name=self.name,
            client=self.client,
            subject_identifiers=subject_identifiers,
            subject_ids=subject_ids,
            member_filter=member_filter,
            act_as_subject=act_as_subject,
        )

    def delete(
        self,
        act_as_subject: Subject | None = None,
    ) -> None:
        delete_groups(
            group_names=[self.name],
            client=self.client,
            act_as_subject=act_as_subject,
        )


@dataclass
class CreateGroup:
    name: str
    display_extension: str
    description: str
    detail: dict[str, Any] | None = None
