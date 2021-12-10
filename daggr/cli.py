import os

import click

from daggr.core.dag import StepState
from daggr.core.runner import Runner

CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.group()
@click.help_option("-h", "--help")
def daggr():
    """DAG Generator & Runtime CLI"""
    # click.echo("Hello")


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--workflow",
    "-w",
    help="Workflow definition file",
    default=f"{os.getcwd()}/workflow.yml",
    show_default=True,
)
@click.option(
    "--format",
    "-f",
    help="Workflow definition file format",
    default=f"yaml",
    show_default=True,
)
@click.option(
    "--runtime",
    "-r",
    help="Runtime that will execute each of the steps",
    default=f"local",
    show_default=True,
)
def run(workflow, format, runtime):
    """Run a DAG from a workflow definition file"""
    r = Runner(format, f"{os.getcwd()}/{workflow}", runtime)
    dag_run = r.run()

    for step_name, data in dag_run.step_runs.items():
        if data.stdout:
            click.echo(f' ======== STDOUT Step "{step_name}" ======== ')
            click.echo(data.stdout)
            click.echo(f" ======== ")

        if data.state == StepState.FAILED:
            click.echo(f' ======== STDERR Step "{step_name}" ======== ')
            click.echo(data.stderr)
            click.echo(f" ======== ")


daggr.add_command(run)
