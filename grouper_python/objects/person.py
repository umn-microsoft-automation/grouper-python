from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from .client import Client
from .subject import Subject


class Person(Subject):
    sourceId: str
    name: str
    attributes: dict[str, str]

    @classmethod
    def from_results(
        cls: type[Person],
        client: Client,
        person_body: dict[str, Any],
        subject_attr_names: list[str],
    ) -> Person:
        attrs = {
            subject_attr_names[i]: person_body["attributeValues"][i]
            for i in range(len(subject_attr_names))
        }
        return cls(
            id=person_body["id"],
            description=person_body.get("description", ""),
            universal_identifier=attrs.get(client.universal_identifier_attr, ""),
            sourceId=person_body["sourceId"],
            name=person_body["name"],
            attributes=attrs,
            client=client,
        )
