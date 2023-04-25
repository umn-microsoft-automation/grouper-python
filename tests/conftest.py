from collections.abc import Iterable

from grouper_python import Client, Group, Stem, Person, Subject
import pytest
from . import data


@pytest.fixture()
def grouper_client() -> Iterable[Client]:
    with Client(data.URI_BASE, "username", "password") as client:
        yield client


@pytest.fixture()
def grouper_group() -> Iterable[Group]:
    with Client(data.URI_BASE, "username", "password") as client:
        group = Group.from_results(client=client, group_body=data.grouper_group_result1)
        yield group


@pytest.fixture()
def grouper_stem() -> Iterable[Stem]:
    with Client(data.URI_BASE, "username", "password") as client:
        stem = Stem.from_results(client=client, stem_body=data.grouper_stem_1)
        yield stem


@pytest.fixture()
def grouper_subject() -> Iterable[Subject]:
    with Client(data.URI_BASE, "username", "password") as client:
        subject = Subject.from_results(
            client=client,
            subject_body=data.ws_subject4,
            subject_attr_names=["description", "name"],
        )
        yield subject


@pytest.fixture()
def grouper_person() -> Iterable[Person]:
    with Client(data.URI_BASE, "username", "password") as client:
        person = Person.from_results(
            client=client,
            person_body=data.ws_subject4,
            subject_attr_names=["description", "name"],
        )
        yield person
