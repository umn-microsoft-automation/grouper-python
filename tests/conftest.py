from collections.abc import Iterable

from grouper_python import GrouperClient
from grouper_python.objects import Group, Stem, Person, Subject
import pytest
from . import data


@pytest.fixture()
def grouper_client() -> Iterable[GrouperClient]:
    with GrouperClient(data.URI_BASE, "username", "password") as client:
        yield client


@pytest.fixture()
def grouper_group() -> Iterable[Group]:
    with GrouperClient(data.URI_BASE, "username", "password") as client:
        group = Group(client=client, group_body=data.grouper_group_result1)
        yield group


@pytest.fixture()
def grouper_stem() -> Iterable[Stem]:
    with GrouperClient(data.URI_BASE, "username", "password") as client:
        stem = Stem(client=client, stem_body=data.grouper_stem_1)
        yield stem


@pytest.fixture()
def grouper_subject() -> Iterable[Subject]:
    with GrouperClient(data.URI_BASE, "username", "password") as client:
        subject = Subject(
            client=client,
            subject_body=data.ws_subject4,
            subject_attr_names=["description", "name"],
        )
        yield subject


@pytest.fixture()
def grouper_person() -> Iterable[Person]:
    with GrouperClient(data.URI_BASE, "username", "password") as client:
        person = Person(
            client=client,
            person_body=data.ws_subject4,
            subject_attr_names=["description", "name"],
        )
        yield person
