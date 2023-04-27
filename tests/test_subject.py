from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grouper_python import Subject
import respx
from httpx import Response
from . import data


def test_subject_equality(grouper_subject: Subject):
    compare = grouper_subject == "a thing"
    assert compare is False


@respx.mock
def test_get_privilege(grouper_subject: Subject):
    respx.route(
        method="POST",
        url=data.URI_BASE + "/grouperPrivileges",
        json=data.get_priv_for_subject_request,
    ).mock(return_value=Response(200, json=data.get_priv_for_subject_result))

    privs = grouper_subject.get_privileges_for_this()

    assert len(privs) == 2
