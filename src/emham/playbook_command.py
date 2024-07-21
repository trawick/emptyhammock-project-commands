import getpass
import sys
from pathlib import Path

import click

from emham.ansible import run_playbook
from emham.roles import install_roles


@click.command()
@click.argument("environment")
def deploy(environment: str) -> None:
    result = install_roles()
    if result:
        print(f"install roles => {result}", file=sys.stderr)
        return
    run_playbook(environment, Path("deploy"))


@click.command()
@click.argument("environment")
@click.argument("playbook_name", type=click.Path())
def run(environment: str, playbook_name: Path) -> None:
    run_playbook(environment, playbook_name)


@click.command()
@click.argument("environment")
@click.argument("username")
@click.option("--ssh-private-key", type=click.Path(exists=True))
def bootstrap(environment: str, username: str, ssh_private_key: str) -> None:
    result = install_roles()
    if result:
        print(f"install roles => {result}", file=sys.stderr)
        return

    extra_playbook_vars = {}

    if ssh_private_key is not None:
        extra_playbook_vars["ansible_ssh_private_key_file"] = ssh_private_key
    else:
        pw = getpass.getpass(f"Password for {username}: ")
        extra_playbook_vars["ansible_ssh_pass"] = pw
        extra_playbook_vars["ansible_ssh_common_args"] = (
            "-o PasswordAuthentication=yes "
            "-o PreferredAuthentications=keyboard-interactive,password "
            "-o PubkeyAuthentication=no"
        )

    run_playbook(
        environment,
        Path("bootstrap"),
        username=username,
        extra_playbook_vars=extra_playbook_vars,
    )


@click.group()
def playbook() -> None:
    pass


playbook.add_command(deploy)
playbook.add_command(run)
playbook.add_command(bootstrap)
