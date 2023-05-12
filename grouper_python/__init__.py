"""grouper_python, a Python package for interacting with Grouper Web Services."""

from .objects.client import GrouperClient

Client = GrouperClient

__version__ = "0.1.3"
__all__ = ["GrouperClient"]
