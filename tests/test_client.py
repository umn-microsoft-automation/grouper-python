from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from grouper_python import Client
from . import data
import respx
from httpx import Response


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
        return_value=Response(200, json=data.find_groups_result_valid_one_group)
    )
    group = grouper_client.get_group("test:GROUP1")

    assert group.name == group.universal_identifier == "test:GROUP1"
    assert group.id == group.uuid == "1ab0482715c74f51bc32822a70bf8f77"
