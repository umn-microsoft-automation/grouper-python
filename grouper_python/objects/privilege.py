from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .client import GrouperClient
from .subject import Subject
from .group import Group
from .stem import Stem


class Privilege:
    def __init__(
        self,
        client: GrouperClient,
        privilege_body: dict[str, Any],
        subject_attr_names: list[str] = [],
    ) -> None:
        self.stem = (
            Stem(client, privilege_body["wsStem"])
            if "wsStem" in privilege_body
            else None
        )
        self.group = (
            Group(client, privilege_body["wsGroup"])
            if "wsGroup" in privilege_body
            else None
        )
        self.target: Stem | Group
        if self.stem:
            self.target = self.stem
        elif self.group:
            self.target = self.group
        else:  # pragma: no cover
            raise ValueError("Unknown target for privilege", privilege_body)
        self.revokable: str = privilege_body["revokable"]
        self.owner_subject = Subject(
            client=client,
            subject_body=privilege_body["ownerSubject"],
            subject_attr_names=subject_attr_names,
        )
        self.allowed: str = privilege_body["allowed"]
        self.subject = Subject(
            client=client,
            subject_body=privilege_body["wsSubject"],
            subject_attr_names=subject_attr_names,
        )
        self.privilege_type: str = privilege_body["privilegeType"]
        self.privilege_name: str = privilege_body["privilegeName"]
