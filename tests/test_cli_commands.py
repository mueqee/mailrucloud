from unittest.mock import patch, MagicMock

import pytest
from click.testing import CliRunner

from cli import cli


@pytest.fixture()
def runner():
    return CliRunner()


class DummyClient(MagicMock):
    pass


@pytest.fixture(autouse=True)
def _patch_network():
    dummy = DummyClient()
    with patch("network.get_client", return_value=dummy):
        yield dummy


def test_ls_default_empty(runner, _patch_network):
    # клиент.list вернёт пустой список
    result = runner.invoke(cli, ["ls"])
    assert result.exit_code == 0


def test_ls_custom_dir(runner, _patch_network):
    _patch_network.list.return_value = ["file.txt"]
    result = runner.invoke(cli, ["ls", "/custom"])
    assert "file.txt" in result.output


def test_rm_ok(runner, _patch_network):
    result = runner.invoke(cli, ["rm", "/x.txt"])
    assert result.exit_code == 0
    _patch_network.clean.assert_called_once() 