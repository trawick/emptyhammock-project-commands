#!/usr/bin/env python

import click

import emham


@click.group()
def cli() -> None:
    pass


cli.add_command(emham.image)
cli.add_command(emham.playbook)
cli.add_command(emham.database)
cli.add_command(emham.media)
cli.add_command(emham.manage)


if __name__ == "__main__":
    cli()
