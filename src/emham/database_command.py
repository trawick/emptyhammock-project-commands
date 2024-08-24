import os
import subprocess
from pathlib import Path

import click

from emham.ansible import read_ansible_var
from emham.inventory import load_inventory
from emham.playbook_command import run_playbook


def _delete_dump_on_server(host: str, port: int, dump_name: Path):
    subprocess.run(
        [
            "ssh",
            "-p",
            str(port),
            host,
            "sudo",
            "rm",
            "-f",
            dump_name
        ],
        check=True,
    )


@click.command()
@click.argument("environment")
def get_dump(environment: str) -> None:
    inventory_data = load_inventory(environment)
    port = 22
    host = inventory_data["webservers"]["hosts"][0]
    dump_name = Path("/tmp") / "project.sql.gz"

    _delete_dump_on_server(host, port, dump_name)
    run_playbook(
        environment, Path("dump_db"), extra_playbook_vars=dict(dumpname=dump_name)
    )

    subprocess.run(
        [
            "scp",
            "-P",
            str(port),
            f"{host}:{dump_name}",
            "."
        ],
        check=True,
    )
    _delete_dump_on_server(host, port, dump_name)


def _get_postgres_envvars(project_name: str) -> dict:
    return {
        "PGUSER": os.environ.get("DB_USER", project_name),
        "PGPASSWORD": os.environ.get("DB_PASSWORD", project_name),
        "PGHOST": os.environ.get("DB_HOST", "localhost"),
        "PGPORT": os.environ.get("DB_PORT", "5432"),
    }


@click.command()
def load_dump() -> None:
    project_name = read_ansible_var("production", "project_name")
    database_name = project_name
    env = _get_postgres_envvars(project_name)
    subprocess.run(
        [
            "dropdb",
            "--if-exists",
            database_name,
        ],
        check=True,
        env=env,
    )
    subprocess.run(
        [
            "createdb",
            "-E",
            "UTF-8",
            database_name,
        ],
        check=True,
        env=env,
    )
    subprocess.run(
        [
            f"zcat project.sql.gz | psql {database_name}"
        ],
        check=True,
        env=env,
        shell=True,
    )


@click.group()
def database() -> None:
    pass


database.add_command(get_dump)
database.add_command(load_dump)
