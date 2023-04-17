from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .group import Group

import httpx
from .util import call_grouper
from .exceptions import GrouperSubjectNotFoundException
from pydantic import BaseModel


class Subject(BaseModel):
    # extension: str
    # displayName: str
    id: str
    description: str = ""
    universal_id: str
    # uuid: str
    # enabled: str
    # displayExtension: str
    # name: str
    # typeOfGroup: str
    # idIndex: str
    # detail: dict[str, Any] | None
    client: httpx.Client

    class Config:
        arbitrary_types_allowed = True

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Subject):
            return NotImplemented
        return self.id == other.id

    def get_groups(
        self,
        stem: str | None = None,
        substems: bool = True,
        act_as_subject_id: str | None = None,
        act_as_subject_identifier: str | None = None,
    ) -> list["Group"]:
        return get_groups_for_subject(
            self.id,
            self.client,
            stem,
            substems,
            act_as_subject_id=act_as_subject_id,
            act_as_subject_identifier=act_as_subject_identifier
        )


def get_groups_for_subject(
    subject_id: str,
    client: httpx.Client,
    stem: str | None = None,
    substems: bool = True,
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> list["Group"]:
    from .group import Group

    body: dict[str, Any] = {
        "WsRestGetMembershipsRequest": {
            "fieldName": "members",
            "wsSubjectLookups": [
                {
                    "subjectId": subject_id,
                }
            ],
            "includeGroupDetail": "T",
        }
    }
    if stem:
        body["WsRestGetMembershipsRequest"]["wsStemLookup"] = {"stemName": stem}
        if substems:
            body["WsRestGetMembershipsRequest"]["stemScope"] = "ALL_IN_SUBTREE"
        else:
            body["WsRestGetMembershipsRequest"]["stemScope"] = "ONE_LEVEL"
    r = call_grouper(
        client,
        "/memberships",
        body,
        act_as_subject_id=act_as_subject_id,
        act_as_subject_identifier=act_as_subject_identifier,
    )
    print(r)
    if "wsGroups" in r["WsGetMembershipsResults"]:
        return [
            Group.from_results(client, grp)
            for grp in r["WsGetMembershipsResults"]["wsGroups"]
        ]
    else:
        return []


def get_subject_by_identifier(
    subject_identifier: str,
    client: httpx.Client,
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
) -> Subject:
    from .user import User

    body = {
        "WsRestGetSubjectsLiteRequest": {
            "subjectIdentifier": subject_identifier,
            "includeSubjectDetail": "T",
        }
    }
    r = call_grouper(
        client,
        "/subjects",
        body,
        act_as_subject_id=act_as_subject_id,
        act_as_subject_identifier=act_as_subject_identifier,
    )
    subject = r["WsGetSubjectsResults"]["wsSubjects"][0]
    if subject["success"] == "F":
        raise GrouperSubjectNotFoundException(subject_identifier)
    if subject["sourceId"] == "g:gsa":
        from .group import get_group_by_name

        return get_group_by_name(subject["name"], client)
    else:
        return User.from_results(
            client=client,
            user_body=subject,
            subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
        )
