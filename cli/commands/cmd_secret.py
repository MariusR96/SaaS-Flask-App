import binascii
import os

import click


@click.command()
@click.argument('bytes', default=128)
def cli(bytes):
    """
    Generate random secret token
    """
    return click.echo(binascii.b2a_hex(os.urandom(bytes)))