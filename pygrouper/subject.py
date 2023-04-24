from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .objects.group import Group
    from .objects.client import Client
    from .objects.subject import Subject

# from .objects.client import Client
# from .util import call_grouper
# from pydantic import BaseModel
from .objects.exceptions import GrouperSubjectNotFoundException
from .group import get_group_by_name


# class Subject(BaseModel):
#     # extension: str
#     # displayName: str
#     id: str
#     description: str = ""
#     universal_id: str
#     # uuid: str
#     # enabled: str
#     # displayExtension: str
#     # name: str
#     # typeOfGroup: str
#     # idIndex: str
#     # detail: dict[str, Any] | None
#     client: Client

#     class Config:
#         arbitrary_types_allowed = True

#     @classmethod
#     def from_results(
#         cls: type[Subject],
#         client: Client,
#         subject_body: dict[str, Any],
#         subject_attr_names: list[str],
#         universal_id_attr: str = "description",
#     ) -> Subject:
#         attrs = {
#             subject_attr_names[i]: subject_body["attributeValues"][i]
#             for i in range(len(subject_attr_names))
#         }
#         return cls(
#             id=subject_body["id"],
#             description=subject_body.get("description", ""),
#             universal_id=attrs.get(universal_id_attr, ""),
#             client=client,
#         )

#     def __hash__(self) -> int:
#         return hash(self.id)

#     def __eq__(self, other: object) -> bool:
#         if not isinstance(other, Subject):
#             return NotImplemented
#         return self.id == other.id

#     def get_groups(
#         self,
#         stem: str | None = None,
#         substems: bool = True,
#         act_as_subject_id: str | None = None,
#         act_as_subject_identifier: str | None = None,
#     ) -> list["Group"]:
#         return get_groups_for_subject(
#             self.id,
#             self.client,
#             stem,
#             substems,
#             act_as_subject_id=act_as_subject_id,
#             act_as_subject_identifier=act_as_subject_identifier,
#         )

#     def is_member(
#         self,
#         group_name: str,
#         member_filter: str = "all",
#         act_as_subject_id: str | None = None,
#         act_as_subject_identifier: str | None = None,
#     ) -> bool:
#         from .group import has_members, HasMember

#         result = has_members(
#             group_name=group_name,
#             client=self.client,
#             subject_ids=[self.id],
#             member_filter=member_filter,
#             act_as_subject_id=act_as_subject_id,
#             act_as_subject_identifier=act_as_subject_identifier,
#         )
#         if result[self.id] == HasMember.IS_MEMBER:
#             return True
#         elif result[self.id] == HasMember.IS_NOT_MEMBER:
#             return False
#         else:
#             raise ValueError


def get_groups_for_subject(
    subject_id: str,
    client: Client,
    stem: str | None = None,
    substems: bool = True,
    act_as_subject: Subject | None = None,
) -> list[Group]:
    from .objects.group import Group

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
    r = client._call_grouper(
        "/memberships",
        body,
        act_as_subject=act_as_subject,
    )
    if "wsGroups" in r["WsGetMembershipsResults"]:
        return [
            Group.from_results(client, grp)
            for grp in r["WsGetMembershipsResults"]["wsGroups"]
        ]
    else:
        return []


def get_subject_by_identifier(
    subject_identifier: str,
    client: Client,
    resolve_group: bool = True,
    attributes: list[str] = [],
    act_as_subject: Subject | None = None
) -> Subject:
    from .objects.person import Person

    attribute_set = set(attributes + [client.universal_identifier_attr, "name"])
    body = {
        "WsRestGetSubjectsRequest": {
            "wsSubjectLookups": [{"subjectIdentifier": subject_identifier}],
            "includeSubjectDetail": "T",
            "subjectAttributeNames": [*attribute_set],
        }
    }
    r = client._call_grouper(
        "/subjects",
        body,
        act_as_subject=act_as_subject
    )
    subject = r["WsGetSubjectsResults"]["wsSubjects"][0]
    if subject["success"] == "F":
        raise GrouperSubjectNotFoundException(subject_identifier)
    if subject["sourceId"] == "g:gsa":
        if resolve_group:
            # from .group import get_group_by_name

            return get_group_by_name(subject["name"], client)
        else:
            return Subject.from_results(
                client=client,
                subject_body=subject,
                subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
            )
    else:
        return Person.from_results(
            client=client,
            person_body=subject,
            subject_attr_names=r["WsGetSubjectsResults"]["subjectAttributeNames"],
        )
