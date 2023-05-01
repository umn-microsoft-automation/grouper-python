from __future__ import annotations
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .client import Client
from pydantic import BaseModel
from .subject import Subject
from .group import Group
from .stem import Stem


class Privilege(BaseModel):
    revokable: str
    owner_subject: Subject
    allowed: str
    stem: Stem | None = None
    group: Group | None = None
    target: Stem | Group
    subject: Subject
    privilege_type: str
    privilege_name: str

    class Config:
        smart_union = True

    @classmethod
    def from_results(
        cls: type[Privilege],
        client: Client,
        privilege_body: dict[str, Any],
        subject_attr_names: list[str] = [],
    ) -> Privilege:
        stem = (
            Stem.from_results(client, privilege_body["wsStem"])
            if "wsStem" in privilege_body
            else None
        )
        group = (
            Group.from_results(client, privilege_body["wsGroup"])
            if "wsGroup" in privilege_body
            else None
        )
        target: Stem | Group
        if stem:
            target = stem
        elif group:
            target = group
        else:  # pragma: no cover
            raise ValueError("Unknown target for privilege", privilege_body)
        return cls(
            revokable=privilege_body["revokable"],
            owner_subject=Subject.from_results(
                client=client,
                subject_body=privilege_body["ownerSubject"],
                subject_attr_names=subject_attr_names,
            ),
            allowed=privilege_body["allowed"],
            stem=stem,
            group=group,
            target=target,
            subject=Subject.from_results(
                client=client,
                subject_body=privilege_body["wsSubject"],
                subject_attr_names=subject_attr_names,
            ),
            privilege_type=privilege_body["privilegeType"],
            privilege_name=privilege_body["privilegeName"],
        )
