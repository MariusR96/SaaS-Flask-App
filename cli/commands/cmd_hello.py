import subprocess

import click


@click.command()
@click.argument('name', default='User')
def cli(name):
    """
    Say hello 
    """

    cmd = 'echo Hello, {0}'.format(name)
    return subprocess.call(cmd, shell=True)