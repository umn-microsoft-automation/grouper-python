from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grouper_python import Client
from grouper_python import Group, Stem, Subject, Person
from . import data
import pytest
import respx
from httpx import Response
from grouper_python.objects.exceptions import (
    GrouperSubjectNotFoundException,
    GrouperStemNotFoundException,
    GrouperGroupNotFoundException,
)


def test_import_and_init():
    from grouper_python import Client

    Client("url", "username", "password")


def test_context_manager():
    from grouper_python import Client

    with Client("url", "username", "password") as client:
        print(client)

    assert client.httpx_client.is_closed is True


def test_close():
    from grouper_python import Client

    client = Client("url", "username", "password")
    assert client.httpx_client.is_closed is False
    client.close()
    assert client.httpx_client.is_closed is True


@respx.mock
def test_get_group(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_one_group_1)
    )
    group = grouper_client.get_group("test:GROUP1")

    assert type(group) is Group


@respx.mock
def test_get_group_not_found(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_no_groups)
    )

    with pytest.raises(GrouperGroupNotFoundException) as excinfo:
        grouper_client.get_group("test:NOT")

    assert excinfo.value.group_name == "test:NOT"


@respx.mock
def test_get_groups(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_two_groups)
    )

    groups = grouper_client.get_groups("GROUP")
    assert len(groups) == 2
    assert type(groups[0]) is Group
    assert type(groups[1]) is Group

    groups = grouper_client.get_groups("GROUP", stem="test")
    assert len(groups) == 2
    assert type(groups[0]) is Group
    assert type(groups[1]) is Group


@respx.mock
def test_get_groups_invalid_stem(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_stem_not_found)
    )

    with pytest.raises(GrouperStemNotFoundException) as excinfo:
        grouper_client.get_groups("GROUP", stem="invalid")

    assert excinfo.value.stem_name == "invalid"


@respx.mock
def test_get_groups_no_groups(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_no_groups)
    )

    groups = grouper_client.get_groups("NOT")
    assert len(groups) == 0


@respx.mock
def test_get_stem(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/stems").mock(
        return_value=Response(200, json=data.find_stem_result_valid_1)
    )
    stem = grouper_client.get_stem("test:child")

    assert type(stem) is Stem
    assert stem.id == stem.uuid == "e2c91c056fb746cca551d6887c722215"
    assert stem.name == "test:child"


@respx.mock
def test_get_subject(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/subjects").mock(
        return_value=Response(200, json=data.get_subject_result_valid_person)
    )
    subject = grouper_client.get_subject("user3333")

    assert type(subject) is Person
    assert isinstance(subject, Subject) is True
    assert subject.id == "abcdefgh3"
    assert subject.description == subject.universal_identifier == "user3333"


@respx.mock
def test_get_subject_is_group(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/subjects").mock(
        return_value=Response(200, json=data.get_subject_result_valid_group)
    )
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_one_group_1)
    )

    subject = grouper_client.get_subject("test:GROUP1")

    assert type(subject) is Group


@respx.mock
def test_get_subject_is_group_not_resolve(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/subjects").mock(
        return_value=Response(200, json=data.get_subject_result_valid_group)
    )
    subject = grouper_client.get_subject("test:GROUP2", resolve_group=False)

    assert type(subject) is Subject


@respx.mock
def test_get_subject_not_found(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/subjects").mock(
        return_value=Response(200, json=data.get_subject_result_subject_not_found)
    )

    with pytest.raises(GrouperSubjectNotFoundException) as excinfo:
        grouper_client.get_subject("notauser")

    assert excinfo.value.subject_identifier == "notauser"


@respx.mock
def test_find_subjects(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/subjects").mock(
        return_value=Response(
            200, json=data.get_subject_result_valid_search_multiple_subjects
        )
    )
    respx.post(url=data.URI_BASE + "/groups").mock(
        return_value=Response(200, json=data.find_groups_result_valid_one_group_1)
    )

    subjects = grouper_client.find_subject("user")
    assert len(subjects) == 3

    subjects = grouper_client.find_subject("user", resolve_group=False)
    assert len(subjects) == 3


@respx.mock
def test_find_subjects_no_result(grouper_client: Client):
    respx.post(url=data.URI_BASE + "/subjects").mock(
        return_value=Response(
            200, json=data.get_subject_result_valid_search_no_results
        )
    )

    subjects = grouper_client.find_subject("user")
    assert len(subjects) == 0
