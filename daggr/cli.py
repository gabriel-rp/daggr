import click


@click.command()
def daggr():
    """DAG Generator & Runtime CLI"""
    click.echo("Hello")


if __name__ == "__main__":
    daggr()
