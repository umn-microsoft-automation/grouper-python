from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grouper_python import Subject


def test_subject_equality(grouper_subject: Subject):
    compare = grouper_subject == "a thing"
    assert compare is False
