from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grouper_python import Subject, Group, GrouperClient
import respx
from httpx import Response
from . import data
import pytest
from grouper_python.privilege import get_privileges
from grouper_python.objects.exceptions import (
    GrouperSubjectNotFoundException,
    GrouperGroupNotFoundException,
    GrouperStemNotFoundException,
)


def test_get_privilege_both_group_and_stem(grouper_subject: Subject):
    with pytest.raises(ValueError) as excinfo:
        grouper_subject.get_privileges_for_this(
            group_name="test:GROUP1", stem_name="test:child"
        )

    assert excinfo.value.args[0] == "Only specify one of group_name or stem_name."


def test_get_privilege_both_subject_id_and_identifier(grouper_group: Group):
    with pytest.raises(ValueError) as excinfo:
        grouper_group.get_privilege_on_this(
            subject_id="abcd1234", subject_identifier="user1234"
        )

    assert (
        excinfo.value.args[0] == "Only specify one of subject_id or subject_identifier."
    )


@respx.mock
def test_get_privilege_subject_identifier(grouper_group: Group):
    respx.route(
        method="POST",
        url=data.URI_BASE + "/grouperPrivileges",
        json=data.get_priv_for_group_with_subject_identifier_request,
    ).mock(return_value=Response(200, json=data.get_priv_for_group_result))

    privs = grouper_group.get_privilege_on_this(subject_identifier="user3333")

    assert len(privs) == 1


@respx.mock
def test_get_privilege_with_privilege_name(grouper_group: Group):
    respx.route(
        method="POST",
        url=data.URI_BASE + "/grouperPrivileges",
        json=data.get_priv_for_group_with_privilege_name_request,
    ).mock(return_value=Response(200, json=data.get_priv_for_group_result))

    privs = grouper_group.get_privilege_on_this(privilege_name="admin")

    assert len(privs) == 1


@respx.mock
def test_get_privilege_with_privilege_type(grouper_subject: Subject):
    respx.route(
        method="POST",
        url=data.URI_BASE + "/grouperPrivileges",
        json=data.get_priv_for_group_with_privilege_type_request,
    ).mock(return_value=Response(200, json=data.get_priv_for_group_result))

    privs = grouper_subject.get_privileges_for_this(privilege_type="access")

    assert len(privs) == 1


def test_get_privileges_no_target(grouper_client: GrouperClient):

    with pytest.raises(ValueError) as excinfo:
        get_privileges(grouper_client)

    assert excinfo.value.args[0] == (
        "Must specify a valid target to retrieve privileges for."
        " Specify either a subject, a stem, a group,"
        " a subject and stem, or a subject and group."
    )


@respx.mock
def test_get_privilege_subject_identifier_not_found(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/grouperPrivileges",).mock(
        return_value=Response(404, json=data.get_priv_result_subject_not_found)
    )

    with pytest.raises(GrouperSubjectNotFoundException) as excinfo:
        grouper_group.get_privilege_on_this(subject_identifier="user3333")

    assert excinfo.value.subject_identifier == "user3333"


@respx.mock
def test_get_privilege_subject_id_not_found(grouper_group: Group):
    respx.post(url=data.URI_BASE + "/grouperPrivileges",).mock(
        return_value=Response(404, json=data.get_priv_result_subject_not_found)
    )

    with pytest.raises(GrouperSubjectNotFoundException) as excinfo:
        grouper_group.get_privilege_on_this(subject_id="abcd1234")

    assert excinfo.value.subject_identifier == "abcd1234"


@respx.mock
def test_get_privilege_group_not_found(grouper_subject: Subject):
    respx.post(url=data.URI_BASE + "/grouperPrivileges",).mock(
        return_value=Response(404, json=data.get_priv_result_group_not_found)
    )

    with pytest.raises(GrouperGroupNotFoundException) as excinfo:
        grouper_subject.get_privileges_for_this(group_name="test:GROUP1")

    assert excinfo.value.group_name == "test:GROUP1"


@respx.mock
def test_get_privilege_stem_not_found(grouper_subject: Subject):
    respx.post(url=data.URI_BASE + "/grouperPrivileges",).mock(
        return_value=Response(404, json=data.get_priv_result_stem_not_found)
    )

    with pytest.raises(GrouperStemNotFoundException) as excinfo:
        grouper_subject.get_privileges_for_this(stem_name="invalid")

    assert excinfo.value.stem_name == "invalid"
