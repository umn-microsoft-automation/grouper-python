from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grouper_python.objects import Subject


def test_object_equality(grouper_subject: Subject):
    compare = grouper_subject == "a thing"
    assert compare is False


def test_dict_output(grouper_subject: Subject):
    assert grouper_subject.dict() == {
        "name": "User 3 Name",
        "id": "abcdefgh3",
        "sourceId": "ldap",
        "description": "user3333",
        "universal_identifier": "user3333",
    }
