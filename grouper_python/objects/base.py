"""grouper_python.objects.base, Base classes that other Grouper objects inherit."""

from __future__ import annotations
from dataclasses import dataclass, fields, field
from copy import deepcopy
from typing import Any, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from .client import GrouperClient


@dataclass(init=False, slots=True)
class GrouperBase:
    """The root of all Grouper objects."""

    client: GrouperClient = field(repr=False)

    def dict(self) -> dict[str, Any]:
        """Return a dictionary representation of this object.

        Note that the GrouperClient object will not be included
        in the dictionary.

        :return: A dictionary representation of this object,
        without the GrouperClient
        :rtype: dict[str, Any]
        """
        return {
            field.name: deepcopy(getattr(self, field.name))
            for field in fields(self)
            if field.repr
        }


@dataclass(init=False, slots=True)
class GrouperEntity(GrouperBase):
    """The root of all Grouper entities."""

    id: str
    description: str
    name: str

    def __hash__(self) -> int:
        """Return a hash of the object's id."""
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        """Compare this object to another."""
        if not isinstance(other, GrouperEntity):
            return NotImplemented
        return self.id == other.id
