import click

from emham.roles import install_roles


@click.command()
def install():
    install_roles()


@click.group()
def roles() -> None:
    pass


roles.add_command(install)
