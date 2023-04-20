from __future__ import annotations

from typing import TYPE_CHECKING, Any
if TYPE_CHECKING:
    from .client import Client
from .subject import Subject


class User(Subject):
    sourceId: str
    name: str
    attributes: dict[str, str]

    @classmethod
    def from_results(
        cls: type[User],
        client: Client,
        user_body: dict[str, Any],
        subject_attr_names: list[str],
        universal_id_attr: str = "description",
    ) -> User:
        attrs = {
            subject_attr_names[i]: user_body["attributeValues"][i]
            for i in range(len(subject_attr_names))
        }
        return cls(
            id=user_body["id"],
            description=user_body.get("description", ""),
            universal_id=attrs.get(universal_id_attr, ""),
            sourceId=user_body["sourceId"],
            name=user_body["name"],
            attributes=attrs,
            client=client,
        )
