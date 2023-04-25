from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grouper_python import Group
from grouper_python.objects.membership import HasMember
from . import data
import respx
from httpx import Response


@respx.mock
def test_get_members(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/memberships").mock(
        return_value=Response(200, json=data.get_membership_result_valid_one_group)
    )
    respx.post(url=data.URI_BASE + "/groups").mock(
        side_effect=[
            Response(200, json=data.get_members_result_valid_one_group),
            Response(200, json=data.find_groups_result_valid_one_group_2),
        ]
    )
    members = grouper_group.get_members()

    assert len(members) == 2


@respx.mock
def test_get_memberships(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/memberships").mock(
        return_value=Response(200, json=data.get_membership_result_valid_one_group)
    )
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_one_group_2)
    )
    memberships = grouper_group.get_memberships()

    assert len(memberships) == 5


@respx.mock
def test_create_privilege(grouper_group: Group):
    respx.route(
        method="POST",
        url=data.URI_BASE + "/grouperPrivileges",
        json=data.create_priv_group_request,
    ).mock(Response(200, json=data.assign_priv_result_valid))

    grouper_group.create_privilege("user3333", "update")


@respx.mock
def test_delete_privilege(grouper_group: Group):
    respx.route(
        method="POST",
        url=data.URI_BASE + "/grouperPrivileges",
        json=data.delete_priv_group_request,
    ).mock(return_value=Response(200, json=data.assign_priv_result_valid))

    grouper_group.delete_privilege("user3333", "update")


@respx.mock
def test_add_members(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.add_member_result_valid)
    )

    grouper_group.add_members(["abcdefgh1"])


@respx.mock
def test_delete_members(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.remove_member_result_valid)
    )

    grouper_group.delete_members(["abcdefgh1"])


@respx.mock
def test_has_members(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups/test:GROUP1/members").mock(
        return_value=Response(200, json=data.has_member_result_identifier)
    )

    has_members = grouper_group.has_members(["user3333"])

    assert has_members["user3333"] == HasMember.IS_MEMBER
    assert has_members["user3333"].value == 1


@respx.mock
def test_delete(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.delete_groups_result_success)
    )

    grouper_group.delete()
