from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grouper_python.objects import Person
from grouper_python.objects import Group
from . import data
import pytest
import respx
from httpx import Response


@respx.mock
def test_get_groups(grouper_person: Person):
    respx.post(url=data.URI_BASE + "/memberships").mock(
        return_value=Response(200, json=data.get_groups_for_subject_result_valid)
    )

    groups = grouper_person.get_groups()
    assert len(groups) == 1
    assert type(groups[0]) is Group

    groups = grouper_person.get_groups(stem="test")
    assert len(groups) == 1
    assert type(groups[0]) is Group

    groups = grouper_person.get_groups(stem="test", substems=False)
    assert len(groups) == 1
    assert type(groups[0]) is Group


@respx.mock
def test_get_groups_no_membership(grouper_person: Person):
    respx.post(url=data.URI_BASE + "/memberships").mock(
        return_value=Response(200, json=data.get_groups_for_subject_no_memberships)
    )

    groups = grouper_person.get_groups()
    assert len(groups) == 0


@respx.mock
def test_is_member_true(grouper_person: Person):
    respx.post(url=data.URI_BASE + "/groups/test:GROUP1/members").mock(
        return_value=Response(200, json=data.has_member_result_id)
    )

    has_member = grouper_person.is_member("test:GROUP1")

    assert has_member is True


@respx.mock
def test_is_member_false(grouper_person: Person):
    respx.post(url=data.URI_BASE + "/groups/test:GROUP2/members").mock(
        return_value=Response(200, json=data.has_member_result_not_member)
    )

    has_member = grouper_person.is_member("test:GROUP2")

    assert has_member is False


@respx.mock
def test_is_member_not_found(grouper_person: Person):
    # This is unlikely to happen, unless someone has manually
    # constructed their Subject rather than building it from a Grouper Result
    respx.post(url=data.URI_BASE + "/groups/test:GROUP2/members").mock(
        return_value=Response(200, json=data.has_member_result_subject_not_found)
    )

    with pytest.raises(ValueError):
        grouper_person.is_member("test:GROUP2")
