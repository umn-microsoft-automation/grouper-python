from __future__ import annotations

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
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
        # universal_id_attr: str = "description",
    ) -> Person:
        attrs = {
            subject_attr_names[i]: person_body["attributeValues"][i]
            for i in range(len(subject_attr_names))
        }
        return cls(
            id=person_body["id"],
            description=person_body.get("description", ""),
            universal_id=attrs.get(client.universal_id_attr, ""),
            sourceId=person_body["sourceId"],
            name=person_body["name"],
            attributes=attrs,
            client=client,
        )
