from click.testing import CliRunner

from daggr.cli import daggr


def test_daggr():
    runner = CliRunner()
    result = runner.invoke(daggr)
    assert result.exit_code == 0


# def test_daggr_run():
#     runner = CliRunner()
#     result = runner.invoke(run, args="-w tests/core/simple_workflow.yml")
#     assert result.exit_code == 0


# def test_daggr_with_example():
#     runner = CliRunner()
#     result = runner.invoke(run, args="-w workflows/examples/simple_workflow/workflow.yml")
#     assert result.exit_code == 0
