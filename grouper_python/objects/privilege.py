"""grouper_python.objects.privilege - Class definition for Privilege."""

from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .client import GrouperClient
from .subject import Subject
from .group import Group
from .stem import Stem
from .base import GrouperBase
from dataclasses import dataclass


@dataclass(slots=True)
class Privilege(GrouperBase):
    """Privilege object representing a Grouper privilege.

    :param client: A GrouperClient object containing connection information
    :type client: GrouperClient
    :param privilege_body: Body of the privilege as returned by the Grouper API
    :type privilege_body: dict[str, Any]
    :param subject_attr_names: Subject attribute names to correspond with
    attribute values from the subject_body, defaults to []
    :type subject_attr_names: list[str], optional
    :raises ValueError: An unknown/unsupported target for the privilege was returned
    by Grouper
    """

    stem: Stem | None
    group: Group | None
    target: Stem | Group
    revokable: str
    owner_subject: Subject
    allowed: str
    subject: Subject
    privilege_name: str
    privilege_type: str

    def __init__(
        self,
        client: GrouperClient,
        privilege_body: dict[str, Any],
        subject_attr_names: list[str] = [],
    ) -> None:
        """Construct a Privilege."""
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
        if self.stem:
            self.target = self.stem
        elif self.group:
            self.target = self.group
        else:  # pragma: no cover
            raise ValueError("Unknown target for privilege", privilege_body)
        self.revokable = privilege_body["revokable"]
        self.owner_subject = Subject(
            client=client,
            subject_body=privilege_body["ownerSubject"],
            subject_attr_names=subject_attr_names,
        )
        self.allowed = privilege_body["allowed"]
        self.subject = Subject(
            client=client,
            subject_body=privilege_body["wsSubject"],
            subject_attr_names=subject_attr_names,
        )
        self.privilege_type = privilege_body["privilegeType"]
        self.privilege_name = privilege_body["privilegeName"]
