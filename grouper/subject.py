from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .group import Group
import httpx
from .util import call_grouper


def get_groups_for_subject(
    subject_id: str,
    client: httpx.Client,
    stem: str | None = None,
    substems: bool = True,
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
    r = call_grouper(client, "/memberships", body)
    return [Group(client, grp) for grp in r["WsGetMembershipsResults"]["wsGroups"]]
