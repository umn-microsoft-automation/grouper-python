from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .client import Client
from .util import call_grouper


def assign_privilege(
    target: str,
    target_type: str,
    privilege_name: str,
    entity_identifier: str,
    allowed: str,
    client: "Client",
    act_as_subject_id: str | None = None,
    act_as_subject_identifier: str | None = None,
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
    call_grouper(
        client.httpx_client,
        "/grouperPrivileges",
        body,
        act_as_subject_id=act_as_subject_id,
        act_as_subject_identifier=act_as_subject_identifier,
    )
