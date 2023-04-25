from grouper_python import Client
import pytest
from .data import URI_BASE


@pytest.fixture()
def grouper_client():
    with Client(URI_BASE, "username", "password") as client:
        yield client
