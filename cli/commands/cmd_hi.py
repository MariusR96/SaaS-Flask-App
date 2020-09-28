import subprocess

import click


@click.command()
@click.option('--name-nick/--no-name-nick', default=False,
              help='Hi, Nick?')
def cli(name_nick):
    """
    Say hi! 
    """
    name_to_say = 'User'

    if name_nick:
        name_to_say = 'Nick'

    cmd = 'echo Hi, {0}!'.format(name_to_say)
    return subprocess.call(cmd, shell=True)