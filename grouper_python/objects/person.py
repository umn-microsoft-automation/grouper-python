"""grouper_python.objects.person - Class definition for Person."""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .client import GrouperClient
from .subject import Subject
from dataclasses import dataclass


@dataclass(eq=False, slots=True)
class Person(Subject):
    """Person object representing a Grouper person.

    :param client: A GrouperClient object containing connection information
    :type client: GrouperClient
    :param person_body: Body of the person as returned by the Grouper API
    :type person_body: dict[str, Any]
    :param subject_attr_names: Subject attribute names for the given person body
    :type subject_attr_names: list[str]
    """

    attributes: dict[str, str]

    def __init__(
        self,
        client: GrouperClient,
        person_body: dict[str, Any],
        subject_attr_names: list[str],
    ) -> None:
        """Construct a Person."""
        attrs = {
            subject_attr_names[i]: person_body["attributeValues"][i]
            for i in range(len(subject_attr_names))
        }
        self.attributes = attrs
        self.id = person_body["id"]
        self.description = attrs.get("description", "")
        self.universal_identifier = attrs.get(client.universal_identifier_attr, "")
        self.sourceId = person_body["sourceId"]
        self.name = person_body["name"]
        self.client = client
        # super().__init__(client, person_body, subject_attr_names)
    # attributes: dict[str, str]

    # @classmethod
    # def from_results(
    #     cls: type[Person],
    #     client: GrouperClient,
    #     person_body: dict[str, Any],
    #     subject_attr_names: list[str],
    # ) -> Person:
    #     attrs = {
    #         subject_attr_names[i]: person_body["attributeValues"][i]
    #         for i in range(len(subject_attr_names))
    #     }
    #     return cls(
    #         id=person_body["id"],
    #         description=attrs.get("description", ""),
    #         universal_identifier=attrs.get(client.universal_identifier_attr, ""),
    #         sourceId=person_body["sourceId"],
    #         name=person_body["name"],
    #         attributes=attrs,
    #         client=client,
    #     )
