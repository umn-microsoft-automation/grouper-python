"""grouper_python.client - Class definition for GrouperClient."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .group import Group
    from .stem import Stem
    from .subject import Subject
    from types import TracebackType
import httpx
from ..util import call_grouper
from ..group import get_group_by_name, find_group_by_name
from ..stem import get_stem_by_name
from ..subject import get_subject_by_identifier, find_subjects


class GrouperClient:
    """Client object for interacting with the grouper API.

    :param grouper_base_url: Base URL for web services in your Grouper instance,
    will end in something like grouper-ws/servicesRest/v2_6_000 where v2_6_000 is
    the version you are targeting.
    :type grouper_base_url: str
    :param username: Username for Basic Auth to Grouper WS
    :type username: str
    :param password: Password for Basic Auth to Grouper WS
    :type password: str
    :param timeout: Timeout for underlying httpx connections, defaults to 30.0
    :type timeout: float, optional
    :param universal_identifier_attr: The subject attribute to treat as a
    "universal" identifer for subjects of type "person".
    This should be the attribute that holds "usernames" for your instance.
    Defaults to "description".
    :type universal_identifier_attr: str, optional
    """

    def __init__(
        self,
        grouper_base_url: str,
        username: str,
        password: str,
        timeout: float = 30.0,
        universal_identifier_attr: str = "description",
    ) -> None:
        """Construct a GrouperClient."""
        self.httpx_client = httpx.Client(
            auth=httpx.BasicAuth(username=username, password=password),
            base_url=grouper_base_url,
            headers={"Content-type": "text/x-json;charset=UTF-8"},
            timeout=timeout,
        )
        self.universal_identifier_attr = universal_identifier_attr

    def __enter__(self) -> GrouperClient:
        """Enter the context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        """Close the underlying httpx Client and exit the context manager."""
        self.httpx_client.close()

    def close(self) -> None:
        """Close the GrouperClient object by closing the underlying httpx Client."""
        self.httpx_client.close()

    def get_group(
        self,
        group_name: str,
        act_as_subject: Subject | None = None,
    ) -> Group:
        """Get a group with the given name.

        :param group_name: The name of the group to get
        :type group_name: str
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :raises GrouperGroupNotFoundException: A group with the given name cannot
        be found
        :return: The group with the given name
        :rtype: Group
        """
        return get_group_by_name(
            group_name=group_name, client=self, act_as_subject=act_as_subject
        )

    def get_groups(
        self,
        group_name: str,
        stem: str | None = None,
        act_as_subject: Subject | None = None,
    ) -> list[Group]:
        """Get groups by approximate name.

        :param group_name: The group name to search for
        :type group_name: str
        :param stem: Optional stem to limit the search to, defaults to None
        :type stem: str | None, optional
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :raises GrouperStemNotFoundException: The specified stem cannot be found
        :raises GrouperSuccessException: An otherwise unhandled issue with the result
        :return: List of found groups, will be an empty list if no groups are found
        :rtype: list[Group]
        """
        return find_group_by_name(
            group_name=group_name, client=self, stem=stem, act_as_subject=act_as_subject
        )

    def get_stem(self, stem_name: str, act_as_subject: Subject | None = None) -> Stem:
        """Get a stem with the given name.

        :param stem_name: The name of the stem to get
        :type stem_name: str
        :param act_as_subject: Optional subject to act as, defaults to None
        :type act_as_subject: Subject | None, optional
        :raises GrouperStemNotFoundException: A stem with the given name cannot be found
        :raises GrouperSuccessException: An otherwise unhandled issue with the result
        :return: The stem with the given name
        :rtype: Stem
        """
        return get_stem_by_name(stem_name, self, act_as_subject=act_as_subject)

    def get_subject(
        self,
        subject_identifier: str,
        resolve_group: bool = True,
        attributes: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> Subject:
        """Get the subject with the given identifier.

        :param subject_identifier:  Identifier of subject to get
        :type subject_identifier: str
        :param resolve_group: Whether to resolve subject that is a group into a Group
        object, which will require an additional API, defaults to True
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
        :return: The subject with the given name
        :rtype: Subject
        """
        return get_subject_by_identifier(
            subject_identifier=subject_identifier,
            client=self,
            resolve_group=resolve_group,
            attributes=attributes,
            act_as_subject=act_as_subject,
        )

    def find_subjects(
        self,
        search_string: str,
        resolve_groups: bool = True,
        attributes: list[str] = [],
        act_as_subject: Subject | None = None,
    ) -> list[Subject]:
        """Find subjects with the given search string.

        :param search_string: Free-form string tos earch for
        :type search_string: str
        :param resolve_groups: Whether to resolve subjects that are groups into Group
        objects, which will require an additional API call, defaults to True
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
        return find_subjects(
            search_string=search_string,
            client=self,
            resolve_groups=resolve_groups,
            attributes=attributes,
            act_as_subject=act_as_subject,
        )

    def _call_grouper(
        self,
        path: str,
        body: dict[str, Any],
        method: str = "POST",
        act_as_subject: Subject | None = None,
    ) -> dict[str, Any]:
        return call_grouper(
            client=self.httpx_client,
            path=path,
            body=body,
            method=method,
            act_as_subject_id=(act_as_subject.id if act_as_subject else None),
        )
