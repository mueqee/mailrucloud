import types
from unittest.mock import MagicMock, patch

import pytest

import api  # module under test


class DummyClient(MagicMock):
    """Минимальный мок WebDAV-клиента с нужными методами."""


@pytest.fixture()
def dummy_client():
    return DummyClient()


@pytest.fixture(autouse=True)
def _patch_network(dummy_client):
    with patch("network.get_client", return_value=dummy_client):
        yield


def test_delete_file_success(dummy_client):
    dummy_client.clean.return_value = None  # не бросает
    assert api.delete_file("/path") is True
    dummy_client.clean.assert_called_once_with("/path")


def test_delete_file_error(dummy_client):
    dummy_client.clean.side_effect = Exception("fail")
    assert api.delete_file("/bad") is False


def test_move_file(dummy_client):
    assert api.move_file("/a", "/b") is True
    dummy_client.move.assert_called_once_with("/a", "/b")


@pytest.mark.parametrize("info_dict", [
    {"size": 123, "modified": "today"},
    {},
])
def test_file_info(dummy_client, info_dict):
    dummy_client.info.return_value = info_dict
    assert api.file_info("/file") == info_dict 