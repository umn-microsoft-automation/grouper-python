from __future__ import annotations
from grouper_python import Stem, Group
from . import data
import respx
from httpx import Response


@respx.mock
def test_create_privilege(grouper_stem: Stem):
    respx.route(
        method="POST",
        url=data.URI_BASE + "/grouperPrivileges",
        json=data.create_priv_stem_request,
    ).mock(Response(200, json=data.assign_priv_result_valid))

    grouper_stem.create_privilege_on_this("user3333", "stemAttrRead")


@respx.mock
def test_delete_privilege(grouper_stem: Stem):
    respx.route(
        method="POST",
        url=data.URI_BASE + "/grouperPrivileges",
        json=data.delete_priv_stem_request,
    ).mock(return_value=Response(200, json=data.assign_priv_result_valid))

    grouper_stem.delete_privilege_on_this("user3333", "stemAttrRead")


@respx.mock
def test_get_privilege(grouper_stem: Stem):
    respx.route(
        method="POST",
        url=data.URI_BASE + "/grouperPrivileges",
        json=data.get_priv_for_stem_request,
    ).mock(return_value=Response(200, json=data.get_priv_for_stem_result))

    privs = grouper_stem.get_privilege_on_this()

    assert len(privs) == 1


@respx.mock
def test_create_child_stem(grouper_stem: Stem):
    respx.post(url=data.URI_BASE + "/stems").mock(
        return_value=Response(200, json=data.create_stems_result_success_one_stem)
    )

    new_stem = grouper_stem.create_child_stem(
        "second", "Second Child Stem", "a second child stem"
    )

    assert type(new_stem) is Stem


@respx.mock
def test_create_child_group(grouper_stem: Stem):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.group_save_result_success_one_group)
    )

    new_group = grouper_stem.create_child_group(
        "GROUP3", "Test3 Display Name", "Group 3 Test description", {"typeNames": []}
    )

    assert type(new_group) is Group


@respx.mock
def test_create_child_group_with_detail(grouper_stem: Stem):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.group_save_result_success_one_group)
    )

    new_group = grouper_stem.create_child_group(
        "GROUP3", "Test3 Display Name", "Group 3 Test description"
    )

    assert type(new_group) is Group


@respx.mock
def test_get_child_stems(grouper_stem: Stem):
    respx.post(url=data.URI_BASE + "/stems").mock(
        return_value=Response(200, json=data.find_stem_result_valid_2)
    )

    stems = grouper_stem.get_child_stems(recursive=True)
    assert len(stems) == 1
    assert type(stems[0]) is Stem

    stems = grouper_stem.get_child_stems(recursive=False)
    assert len(stems) == 1
    assert type(stems[0]) is Stem


@respx.mock
def test_get_child_groups(grouper_stem: Stem):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_one_group_3)
    )

    groups = grouper_stem.get_child_groups(recursive=True)
    assert len(groups) == 1
    assert type(groups[0]) is Group

    groups = grouper_stem.get_child_groups(recursive=False)
    assert len(groups) == 1
    assert type(groups[0]) is Group

    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_no_groups)
    )
    groups = grouper_stem.get_child_groups(recursive=True)
    assert len(groups) == 0


@respx.mock
def test_delete(grouper_stem: Stem):
    respx.post(url=data.URI_BASE + "/stems").mock(
        return_value=Response(200, json=data.delete_stem_result_success)
    )

    grouper_stem.delete()
