from __future__ import annotations

from enum import Enum, StrEnum, auto
from .subject import Subject
from pydantic import BaseModel


class HasMember(Enum):
    IS_MEMBER = 1
    IS_NOT_MEMBER = 2
    SUBJECT_NOT_FOUND = 3


class MembershipType(StrEnum):
    DIRECT = auto()
    INDIRECT = auto()


class MemberType(StrEnum):
    USER = auto()
    GROUP = auto()


class Membership(BaseModel):
    member: Subject
    member_type: MemberType
    membership_type: MembershipType
