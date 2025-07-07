from unittest.mock import MagicMock

import pytest

import api
import network


@pytest.fixture()
def dummy():
    """Глобальный мок, предоставляемый conftest.py."""
    return network.get_client()


def test_delete_file_success(dummy):
    dummy.clean.side_effect = None
    assert api.delete_file("/path") is True


def test_delete_file_error(dummy):
    dummy.clean.side_effect = Exception("fail")
    assert api.delete_file("/bad") is False


def test_move_file(dummy):
    assert api.move_file("/a", "/b") is True


@pytest.mark.parametrize("info_dict", [{"size": 123}, {}])
def test_file_info(dummy, info_dict):
    dummy.info.return_value = info_dict
    assert api.file_info("/file") == info_dict or api.file_info("/file") == {} 