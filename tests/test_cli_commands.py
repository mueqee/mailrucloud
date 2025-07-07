from click.testing import CliRunner

import pytest

from cli import cli


@pytest.fixture()
def runner():
    return CliRunner()


def test_ls_default_empty(runner):
    result = runner.invoke(cli, ["ls"])
    assert result.exit_code == 0


def test_ls_custom_dir(runner):
    result = runner.invoke(cli, ["ls", "/custom"])
    assert result.exit_code == 0


def test_rm_ok(runner):
    result = runner.invoke(cli, ["rm", "/x.txt"])
    assert result.exit_code == 0 