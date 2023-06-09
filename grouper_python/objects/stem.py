"""grouper_python.objects.stem - Class definition for Stem and related objects."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .subject import Subject
    from .group import Group
    from .privilege import Privilege

from ..privilege import assign_privilege, get_privileges
from ..stem import create_stems, get_stems_by_parent, delete_stems
from ..group import create_groups, get_groups_by_parent
from .client import GrouperClient
from dataclasses import dataclass
from .base import GrouperEntity


@dataclass(slots=True, eq=False)
class Stem(GrouperEntity):
    """Stem object representing a Grouper stem.

    :param client: A GrouperClient object containing connection information
    :type client: GrouperClient
    :param stem_body: Body of the stem as returned by the Grouper API
    :type stem_body: dict[str, Any]
    """

    extension: str
    displayName: str
    uuid: str
    displayExtension: str
    idIndex: str

    def __init__(
        self,
        client: GrouperClient,
        stem_body: dict[str, Any],
    ) -> None:
        """Construct a Stem."""
        self.id = stem_body["uuid"]
        self.description = stem_body.get("description", "")
        self.extension = stem_body["extension"]
        self.displayName = stem_body["displayName"]
        self.uuid = stem_body["uuid"]
        self.displayExtension = stem_body["displayExtension"]
        self.name = stem_body["name"]
        self.idIndex = stem_body["idIndex"]
        self.client = client

    def create_privilege_on_this(
        self,
        entity_identifier: str,
        privilege_name: str,
        act_as_subject: Subject | None = None,
    ) -> None:
        """Create a privilege on this Stem.

        :param entity_identifier: Identifier of the entity to receive the permission
        :type entity_identifier: str
        :param privilege_name: Name of the privilege to assign
        :type privilege_name: str
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        """
        assign_privilege(
            target=self.name,
            target_type="stem",
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
        """Delete a privilege on this Stem.

        :param entity_identifier: Identifier of the entity to remove permission for
        :type entity_identifier: str
        :param privilege_name: Name of the privilege to delete
        :type privilege_name: str
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        """
        assign_privilege(
            target=self.name,
            target_type="stem",
            privilege_name=privilege_name,
            entity_identifier=entity_identifier,
            allowed="F",
            client=self.client,
            act_as_subject=act_as_subject,
        )

    def get_privileges_on_this(
        self,
        subject_id: str | None = None,
        subject_identifier: str | None = None,
        privilege_name: str | None = None,
        attributes: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> list[Privilege]:
        """Get privileges on this Stem.

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
        :return: List of retreived privileges on this Stem
        satisfying the given constraints
        :rtype: list[Privilege]
        """
        return get_privileges(
            client=self.client,
            subject_id=subject_id,
            subject_identifier=subject_identifier,
            stem_name=self.name,
            privilege_name=privilege_name,
            attributes=attributes,
            act_as_subject=act_as_subject,
        )

    def create_child_stem(
        self,
        extension: str,
        display_extension: str,
        description: str = "",
        act_as_subject: Subject | None = None,
    ) -> Stem:
        """Create a child stem in this Stem.

        :param extension: The extension (id) of the stem to create.
        :type extension: str
        :param display_extension: The display extension (display name)
        of the stem to create
        :type display_extension: str
        :param description: Description of the stem to create, defaults to ""
        :type description: str, optional
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :return: A Stem object representing the newly created stem
        :rtype: Stem
        """
        create = CreateStem(
            name=f"{self.name}:{extension}",
            displayExtension=display_extension,
            description=description,
        )
        return create_stems(
            [create],
            self.client,
            act_as_subject=act_as_subject,
        )[0]

    def create_child_group(
        self,
        extension: str,
        display_extension: str,
        description: str = "",
        detail: dict[str, Any] | None = None,
        act_as_subject: Subject | None = None,
    ) -> Group:
        """Create a child group in this Stem.

        :param extension: The extension (id) of the group to create.
        :type extension: str
        :param display_extension: The display extension (display name)
        of the group to create
        :type display_extension: str
        :param description: Description of the group to create, defaults to ""
        :type description: str, optional
        :param detail: Dict of "details" of the group to create, defaults to None
        :type detail: dict[str, Any] | None, optional
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :return: A Group object representing the newly created group
        :rtype: Group
        """
        from .group import CreateGroup

        create = CreateGroup(
            name=f"{self.name}:{extension}",
            display_extension=display_extension,
            description=description,
            detail=detail,
        )
        return (create_groups([create], self.client, act_as_subject))[0]

    def get_child_stems(
        self,
        recursive: bool,
        act_as_subject: Subject | None = None,
    ) -> list[Stem]:
        """Get child stems of this Stem.

        :param recursive: Whether to look recursively through the entire subtree (True),
        or only one level in this stem (False)
        :type recursive: bool
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :return: The list of Stems found
        :rtype: list[Stem]
        """
        return get_stems_by_parent(
            parent_name=self.name,
            client=self.client,
            recursive=recursive,
            act_as_subject=act_as_subject,
        )

    def get_child_groups(
        self,
        recursive: bool,
        act_as_subject: Subject | None = None,
    ) -> list[Group]:
        """Get child groups of this Stem.

        :param recursive: Whether to look recursively through the entire subtree (True),
        or only one level in this stem (False)
        :type recursive: bool
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :return: The list of Groups found
        :rtype: list[Group]
        """
        return get_groups_by_parent(
            parent_name=self.name,
            client=self.client,
            recursive=recursive,
            act_as_subject=act_as_subject,
        )

    def delete(
        self,
        act_as_subject: Subject | None = None,
    ) -> None:
        """Delete this Stem.

        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        """
        delete_stems(
            stem_names=[self.name], client=self.client, act_as_subject=act_as_subject
        )


@dataclass
class CreateStem:
    """Class representing all data needed to create a new Grouper stem.

    :param name: Full name (ID path) of the stem to create
    :type name: str
    :param display_extension: Display extension (display name) of the stem to create
    :type display_extension: str
    :param description: Description of the stem to create
    :type description: str
    """

    name: str
    displayExtension: str
    description: str
