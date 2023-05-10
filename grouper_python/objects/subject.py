"""grouper_python.objects.subject - Class definition for Subject."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .group import Group
    from .privilege import Privilege
    from .client import GrouperClient
from ..subject import get_groups_for_subject
from ..membership import has_members
from ..privilege import get_privileges
from dataclasses import dataclass
from .base import GrouperEntity
from .exceptions import GrouperSubjectNotFoundException


@dataclass(slots=True, eq=False)
class Subject(GrouperEntity):
    """Subject object representing a Grouper subject.

    :param client: A GrouperClient object containing connection information
    :type client: GrouperClient
    :param subject_body: Body of the subject as returned by the Grouper API
    :type subject_body: dict[str, Any]
    :param subject_attr_names: Subject attribute names to correspond with
    attribute values from the subject_body
    :type subject_attr_names: list[str]
    """

    universal_identifier: str
    sourceId: str

    def __init__(
        self,
        client: GrouperClient,
        subject_body: dict[str, Any],
        subject_attr_names: list[str],
    ) -> None:
        """Construct a Subject."""
        attrs = {
            subject_attr_names[i]: subject_body["attributeValues"][i]
            for i in range(len(subject_attr_names))
        }
        if subject_body["sourceId"] == "g:gsa":
            universal_identifier_attr = "name"
        else:
            universal_identifier_attr = client.universal_identifier_attr
        self.id = subject_body["id"]
        self.description = attrs.get("description", "")
        self.universal_identifier = attrs[universal_identifier_attr]
        self.sourceId = subject_body["sourceId"]
        self.name = subject_body["name"]
        self.client = client

    def get_groups(
        self,
        stem: str | None = None,
        substems: bool = True,
        act_as_subject: Subject | None = None,
    ) -> list[Group]:
        """Get groups this subject is a member of.

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
        return get_groups_for_subject(
            self.id,
            self.client,
            stem,
            substems,
            act_as_subject=act_as_subject,
        )

    def is_member(
        self,
        group_name: str,
        member_filter: str = "all",
        act_as_subject: Subject | None = None,
    ) -> bool:
        """Check if this subject is a member of the given group.

        :param group_name: Name of group to check for membership.
        :type group_name: str
        :param member_filter: Type of mebership to check for
        (all, immediate, effective), defaults to "all"
        :type member_filter: str, optional
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :raises GrouperSubjectNotFoundException: This subject cannot be found
        :raises GrouperGroupNotFoundException: A group with the given name cannot
        be found
        :raises GrouperSuccessException: An otherwise unhandled issue with the result
        :return: If the user is a member of the group (True) or not (False)
        :rtype: bool
        """
        from .membership import HasMember

        result = has_members(
            group_name=group_name,
            client=self.client,
            subject_ids=[self.id],
            member_filter=member_filter,
            act_as_subject=act_as_subject,
        )
        if result[self.id] == HasMember.IS_MEMBER:
            return True
        elif result[self.id] == HasMember.IS_NOT_MEMBER:
            return False
        else:
            raise GrouperSubjectNotFoundException(
                subject_identifier=self.universal_identifier
            )

    def get_privileges_for_this_in_others(
        self,
        group_name: str | None = None,
        stem_name: str | None = None,
        privilege_name: str | None = None,
        privilege_type: str | None = None,
        attributes: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> list[Privilege]:
        """Get privileges this subject has in other objects.

        :param group_name: Group name to limit privileges to,
        cannot be specified if stem_name is specified, defaults to None
        :type group_name: str | None, optional
        :param stem_name: Stem name to limit privileges to,
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
        :raises GrouperGroupNotFoundException: A group with the given name cannot
        be found
        :raises GrouperStemNotFoundException: A stem with the given name cannot be found
        :raises GrouperSuccessException: An otherwise unhandled issue with the result
        :return: A list of retreived privileges for this subject
        satisfying any given constraints
        :rtype: list[Privilege]
        """
        return get_privileges(
            client=self.client,
            subject_id=self.id,
            group_name=group_name,
            stem_name=stem_name,
            privilege_name=privilege_name,
            privilege_type=privilege_type,
            attributes=attributes,
            act_as_subject=act_as_subject,
        )
