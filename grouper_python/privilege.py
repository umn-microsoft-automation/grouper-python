from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .objects.client import Client
    from .objects.subject import Subject


def assign_privilege(
    target: str,
    target_type: str,
    privilege_name: str,
    entity_identifier: str,
    allowed: str,
    client: Client,
    act_as_subject: Subject | None = None,
) -> None:
    body = {
        "WsRestAssignGrouperPrivilegesLiteRequest": {
            "allowed": allowed,
            "privilegeName": privilege_name,
            "subjectIdentifier": entity_identifier,
        }
    }
    if target_type == "stem":
        body["WsRestAssignGrouperPrivilegesLiteRequest"]["stemName"] = target
        body["WsRestAssignGrouperPrivilegesLiteRequest"]["privilegeType"] = "naming"
    elif target_type == "group":
        body["WsRestAssignGrouperPrivilegesLiteRequest"]["groupName"] = target
        body["WsRestAssignGrouperPrivilegesLiteRequest"]["privilegeType"] = "access"
    else:  # pragma: no cover
        pass
    client._call_grouper(
        "/grouperPrivileges",
        body,
        act_as_subject=act_as_subject,
    )