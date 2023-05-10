"""grouper_python.objects.membership - Objects related to Grouper membership."""

from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:  # pragma: no cover
    from .subject import Subject
from enum import Enum, StrEnum, auto
from dataclasses import dataclass


class HasMember(Enum):
    """Enum of results for has_member."""

    IS_MEMBER = 1
    IS_NOT_MEMBER = 2
    SUBJECT_NOT_FOUND = 3


class MembershipType(StrEnum):
    """Enum of membership types."""

    DIRECT = auto()
    INDIRECT = auto()


class MemberType(StrEnum):
    """Enum of member types."""

    PERSON = auto()
    GROUP = auto()


@dataclass
class Membership:
    """Class representing a Grouper membership."""

    member: Subject
    member_type: MemberType
    membership_type: MembershipType
