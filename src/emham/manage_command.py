import subprocess

import click

from emham.ansible import get_ssh_host_port, read_ansible_var


@click.command()
@click.argument("environment")
@click.argument("remaining_args", nargs=-1)
def remote(environment: str, remaining_args: tuple) -> None:
    host, port = get_ssh_host_port(environment)
    script_dir = read_ansible_var(environment, "script_dir")

    subprocess.run(
        [
            "ssh",
            "-tt",
            "-p",
            str(port),
            host,
            f"{script_dir}/manage.sh",
        ]
        + list(remaining_args),
        check=True,
        capture_output=False,
    )


@click.group()
def manage() -> None:
    pass


manage.add_command(remote)
