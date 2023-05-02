"""In addition to testing call_grouper in util, this will test some code paths in
other functions that are only reachable when called directly, rather than through
an existing object."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grouper_python import GrouperClient, Person
import respx
from httpx import Response
from . import data
import pytest
from grouper_python.util import call_grouper
from grouper_python.privilege import assign_privilege
from grouper_python.membership import has_members, get_members_for_groups
from grouper_python.objects.exceptions import (
    GrouperAuthException,
    GrouperGroupNotFoundException,
)


def test_both_act_as_id_and_identifier(grouper_client: GrouperClient):
    with pytest.raises(ValueError) as excinfo:
        call_grouper(
            grouper_client.httpx_client,
            "/path",
            {},
            act_as_subject_id="abcd1234",
            act_as_subject_identifier="user1234",
        )
    assert (
        excinfo.value.args[0]
        == "Only one of act_as_subject_id or act_as_subject_identifier should be"
        " specified"
    )


@respx.mock
def test_act_as_subject_lite(grouper_client: GrouperClient, grouper_person: Person):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_one_group_1)
    )
    grouper_client.get_group("test:GROUP1", act_as_subject=grouper_person)


@respx.mock
def test_act_as_subject_notlite(grouper_client: GrouperClient, grouper_person: Person):
    respx.post(url=data.URI_BASE + "/subjects").mock(
        return_value=Response(200, json=data.get_subject_result_valid_person)
    )
    grouper_client.get_subject("user3333", act_as_subject=grouper_person)


@respx.mock
def test_act_as_id_lite(grouper_client: GrouperClient):
    orig_body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": "test:GROUP1",
            "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
            "includeGroupDetail": "T",
        }
    }
    body_with_auth = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": "test:GROUP1",
            "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
            "includeGroupDetail": "T",
            "actAsSubjectId": "abcd1234",
        }
    }
    respx.route(method="POST", url=data.URI_BASE + "/groups", json=body_with_auth).mock(
        return_value=Response(200, json=data.find_groups_result_valid_one_group_1)
    )
    call_grouper(
        grouper_client.httpx_client,
        path="/groups",
        body=orig_body,
        act_as_subject_id="abcd1234",
    )


@respx.mock
def test_act_as_identifier_lite(grouper_client: GrouperClient):
    orig_body = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": "test:GROUP1",
            "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
            "includeGroupDetail": "T",
        }
    }
    body_with_auth = {
        "WsRestFindGroupsLiteRequest": {
            "groupName": "test:GROUP1",
            "queryFilterType": "FIND_BY_GROUP_NAME_EXACT",
            "includeGroupDetail": "T",
            "actAsSubjectIdentifier": "user1234",
        }
    }
    respx.route(method="POST", url=data.URI_BASE + "/groups", json=body_with_auth).mock(
        return_value=Response(200, json=data.find_groups_result_valid_one_group_1)
    )
    call_grouper(
        grouper_client.httpx_client,
        path="/groups",
        body=orig_body,
        act_as_subject_identifier="user1234",
    )


@respx.mock
def test_act_as_id_notlite(grouper_client: GrouperClient):
    orig_body = {
        "WsRestGetSubjectsRequest": {
            "wsSubjectLookups": [{"subjectIdentifier": "user1234"}],
            "includeSubjectDetail": "T",
        }
    }
    body_with_auth = {
        "WsRestGetSubjectsRequest": {
            "wsSubjectLookups": [{"subjectIdentifier": "user1234"}],
            "includeSubjectDetail": "T",
            "actAsSubjectLookup": {"subjectId": "abcd1234"},
        }
    }
    respx.route(
        method="POST", url=data.URI_BASE + "/subjects", json=body_with_auth
    ).mock(return_value=Response(200, json=data.get_subject_result_valid_person))
    call_grouper(
        grouper_client.httpx_client,
        path="subjects",
        body=orig_body,
        act_as_subject_id="abcd1234",
    )


@respx.mock
def test_act_as_identifier_notlite(grouper_client: GrouperClient):
    orig_body = {
        "WsRestGetSubjectsRequest": {
            "wsSubjectLookups": [{"subjectIdentifier": "user1234"}],
            "includeSubjectDetail": "T",
        }
    }
    body_with_auth = {
        "WsRestGetSubjectsRequest": {
            "wsSubjectLookups": [{"subjectIdentifier": "user1234"}],
            "includeSubjectDetail": "T",
            "actAsSubjectLookup": {"subjectIdentifier": "user1234"},
        }
    }
    respx.route(
        method="POST", url=data.URI_BASE + "/subjects", json=body_with_auth
    ).mock(return_value=Response(200, json=data.get_subject_result_valid_person))
    call_grouper(
        grouper_client.httpx_client,
        path="subjects",
        body=orig_body,
        act_as_subject_identifier="user1234",
    )


@respx.mock
def test_grouper_auth_exception(grouper_client: GrouperClient):
    """validate that a 401 (auth issue) from the grouper API is properly caught"""
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(401, text="<html>Unauthorized</html>")
    )

    with pytest.raises(GrouperAuthException):
        call_grouper(grouper_client.httpx_client, body={}, path="/groups")


@respx.mock
def test_assign_privilege_unknown_target_type(grouper_client: GrouperClient):
    with pytest.raises(ValueError) as excinfo:
        assign_privilege(
            "target:name", "type", "update", "user1234", "T", grouper_client
        )
    assert (
        excinfo.value.args[0]
        == "Target type must be either 'stem' or 'group', but got 'type'."
    )


@respx.mock
def test_has_members_no_subject(grouper_client: GrouperClient):
    with pytest.raises(ValueError) as excinfo:
        has_members("target:name", grouper_client)
    assert (
        excinfo.value.args[0]
        == "At least one of subject_identifiers or subject_ids must be specified"
    )


@respx.mock
def test_get_members_second_group_not_found(grouper_client: GrouperClient):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(
            200, json=data.get_members_result_multiple_groups_second_group_not_found
        )
    )
    with pytest.raises(GrouperGroupNotFoundException) as excinfo:
        get_members_for_groups(["test:GROUP1", "test:NOT"], grouper_client)

    assert excinfo.value.group_name == "test:NOT"
