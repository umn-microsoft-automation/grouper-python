from collections.abc import Iterable

from grouper_python import Client, Group, Stem
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
