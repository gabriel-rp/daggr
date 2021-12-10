from click.testing import CliRunner

from daggr.cli import daggr


def test_daggr():
    runner = CliRunner()
    result = runner.invoke(daggr)
    assert result.exit_code == 0


def test_daggr_run():
    runner = CliRunner()
    result = runner.invoke(daggr)
    assert result.exit_code == 0
