from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .group import Group

import httpx
from .group import get_group_by_name
from .util import call_grouper
from .subject import get_groups_for_subject


class User:
    def __init__(
        self,
        client: httpx.Client,
        user_body: dict[str, str],
        subject_attr_names: list[str],
    ) -> None:
        self.client = client
        self.sourceId = user_body["sourceId"]
        self.name = user_body["name"]
        self.id = user_body["id"]
        attrs = {}
        for n in range(len(subject_attr_names)):
            attrs[subject_attr_names[n]] = user_body["attributeValues"][n]
        self.attributes = attrs
        self.description = attrs["description"]

    def get_groups(
        self, stem: str | None = None, substems: bool = True
    ) -> list["Group"]:
        return get_groups_for_subject(self.id, self.client, stem, substems)


def get_subject_by_identifier(
    subject_identifier: str, client: httpx.Client
) -> Union[User, "Group"]:
    body = {
        "WsRestGetSubjectsLiteRequest": {
            "subjectIdentifier": subject_identifier,
            "includeSubjectDetail": "T",
        }
    }
    r = call_grouper(client, "/subjects", body)
    subject = r["WsGetSubjectsResults"]["wsSubjects"][0]
    if subject["sourceId"] == "g:gsa":
        return get_group_by_name(subject["name"], client)
    else:
        return User(
            client=client,
            user_body=subject,
            subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
        )
