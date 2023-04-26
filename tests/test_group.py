from __future__ import annotations
from grouper_python.objects.membership import HasMember
from grouper_python.objects.exceptions import (
    GrouperPermissionDenied,
    GrouperGroupNotFoundException,
)
from grouper_python import Person, Group, Subject
from . import data
import pytest
import respx
from httpx import Response


@respx.mock
def test_get_members(grouper_group: Group):
    group_call = respx.post(url=data.URI_BASE + "/groups").mock(
        side_effect=[
            Response(200, json=data.get_members_result_valid_one_group),
            Response(200, json=data.find_groups_result_valid_one_group_2),
        ]
    )
    members = grouper_group.get_members()
    assert len(members) == 2
    assert group_call.call_count == 2

    group_call = respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.get_members_result_valid_one_group)
    )
    members = grouper_group.get_members(resolve_groups=False)
    assert len(members) == 2
    # Call count is cumulative for the test, so it was called twice before,
    # and should be called once more, for a total of 3
    assert group_call.call_count == 3


@respx.mock
def test_get_members_valid_no_members(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.get_members_result_empty)
    )

    members = grouper_group.get_members(resolve_groups=False)
    assert len(members) == 0


@respx.mock
def test_get_members_group_not_found(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.get_members_result_group_not_found)
    )

    with pytest.raises(GrouperGroupNotFoundException) as excinfo:
        grouper_group.get_members()

    assert excinfo.value.group_name == "test:NOT"

    # members = grouper_group.get_members(resolve_groups=False)
    # assert len(members) == 0


@respx.mock
def test_get_memberships(grouper_group: Group):
    membership_call = respx.post(url=data.URI_BASE + "/memberships").mock(
        return_value=Response(200, json=data.get_membership_result_valid_one_group)
    )
    group_call = respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_one_group_2)
    )
    memberships = grouper_group.get_memberships()
    assert len(memberships) == 5
    membership_types = {"Person": 0, "Group": 0}
    for m in memberships:
        print(type(m.member))
        if type(m.member) is Person:
            membership_types["Person"] = membership_types["Person"] + 1
        elif type(m.member) is Group:
            membership_types["Group"] = membership_types["Group"] + 1
    # When resolving groups (the default) this result should have 4 Persons and 1 Group
    assert membership_types["Person"] == 4
    assert membership_types["Group"] == 1

    memberships = grouper_group.get_memberships(resolve_groups=False)
    assert len(memberships) == 5
    membership_types = {"Person": 0, "Subject": 0}
    for m in memberships:
        print(type(m.member))
        if type(m.member) is Person:
            membership_types["Person"] = membership_types["Person"] + 1
        elif type(m.member) is Subject:
            membership_types["Subject"] = membership_types["Subject"] + 1
    # When not resolving groups, this result should have 4 Persons and 1 Subject
    assert membership_types["Person"] == 4
    assert membership_types["Subject"] == 1

    # The Membership endpoint should be called twice, once each for each
    # get_memberships() call
    assert membership_call.call_count == 2
    # The group call endpoint should only be called once, for the first
    # call to get_memberships() where groups are resolved
    # In the second call, groups are not resolved, so the group is returned
    # as a subject instead, and the groups endpoint isn't called.
    assert group_call.call_count == 1


@respx.mock
def test_get_memberships_group_not_found(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/memberships").mock(
        return_value=Response(200, json=data.get_membership_result_group_not_found)
    )

    with pytest.raises(GrouperGroupNotFoundException) as excinfo:
        grouper_group.get_memberships()

    assert excinfo.value.group_name == "test:NOT"


@respx.mock
def test_get_memberships_valid_no_memberships(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/memberships").mock(
        return_value=Response(200, json=data.get_membership_result_valid_no_memberships)
    )

    memberships = grouper_group.get_memberships()

    assert len(memberships) == 0


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
def test_add_members_group_not_found(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.add_member_result_group_not_found)
    )

    with pytest.raises(GrouperGroupNotFoundException) as excinfo:
        grouper_group.add_members(["user3333"])

    assert excinfo.value.group_name == "test:GROUP1"


@respx.mock
def test_add_members_permission_denied(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.add_member_result_permission_denied)
    )

    with pytest.raises(GrouperPermissionDenied):
        grouper_group.add_members(["user3333"])


@respx.mock
def test_delete_members(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.remove_member_result_valid)
    )

    grouper_group.delete_members(["abcdefgh1"])


@respx.mock
def test_delete_members_group_not_found(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.remove_member_result_group_not_found)
    )

    with pytest.raises(GrouperGroupNotFoundException) as excinfo:
        grouper_group.delete_members(["user3333"])

    assert excinfo.value.group_name == "test:GROUP1"


@respx.mock
def test_delete_members_permission_denied(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.remove_member_result_permission_denied)
    )

    with pytest.raises(GrouperPermissionDenied):
        grouper_group.delete_members(["user3333"])


@respx.mock
def test_has_members(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups/test:GROUP1/members").mock(
        return_value=Response(200, json=data.has_member_result_identifier)
    )

    has_members = grouper_group.has_members(["user3333"])

    assert has_members["user3333"] == HasMember.IS_MEMBER
    assert has_members["user3333"].value == 1


@respx.mock
def test_has_members_group_not_found(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups/test:GROUP1/members").mock(
        return_value=Response(200, json=data.has_member_result_group_not_found)
    )

    with pytest.raises(GrouperGroupNotFoundException) as excinfo:
        grouper_group.has_members(["user3333"])

    assert excinfo.value.group_name == "test:GROUP1"

    # has_members = grouper_group.has_members(["user3333"])

    # assert has_members["user3333"] == HasMember.IS_MEMBER
    # assert has_members["user3333"].value == 1


@respx.mock
def test_delete(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.delete_groups_result_success)
    )

    grouper_group.delete()


@respx.mock
def test_delete_permission_denied(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.delete_groups_permission_denied)
    )

    with pytest.raises(GrouperPermissionDenied):
        grouper_group.delete()


@respx.mock
def test_delete_group_not_found(grouper_group: Group):
    # This is unlikely to happen, unless the Group was
    # manually construted. However this does test the code
    # in the underlying method for when a group isn't found
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.delete_groups_group_not_found)
    )

    with pytest.raises(GrouperGroupNotFoundException) as excinfo:
        grouper_group.delete()

    assert excinfo.value.group_name == "test:GROUP1"
