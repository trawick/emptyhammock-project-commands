import os
import subprocess

import click

from emham.ansible import read_ansible_var, get_ssh_host_port


@click.command()
@click.argument("environment")
def get_media(environment: str) -> None:
    host, port = get_ssh_host_port(environment)

    media_dir = read_ansible_var(environment, "media_dir")
    if not media_dir.endswith("/"):
        media_dir += "/"

    if not os.path.exists("media"):
        os.mkdir("media")

    subprocess.run(
        [
            "rsync",
            "-arvz",
            "-delete",
            "-e",
            f"ssh -p {port}",
            f"{host}:{media_dir}",
            "./media/",
        ],
        check=True,
        capture_output=False,
    )


@click.group()
def media() -> None:
    pass


media.add_command(get_media)
