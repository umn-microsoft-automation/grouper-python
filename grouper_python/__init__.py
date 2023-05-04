"""grouper_python, a Python package for interacting with Grouper Web Services."""

from .objects.client import GrouperClient
from .objects.group import Group
from .objects.stem import Stem
from .objects.subject import Subject
from .objects.person import Person

Client = GrouperClient

__version__ = "0.1.1"

__all__ = ["GrouperClient", "Group", "Stem", "Subject", "Person"]
