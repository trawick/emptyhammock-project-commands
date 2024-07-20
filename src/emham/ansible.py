import json
import os
import re
import subprocess
from pathlib import Path

from emham.inventory import load_inventory


def read_ansible_var(environment: str, variable: str):
    inventory_file = os.path.abspath(os.path.join("deploy", "inventory", environment))
    result = subprocess.run(
        [
            "ansible",
            "-i",
            inventory_file,
            "webservers",
            "-e",
            "@environments/all/vars.yml",
            "-e",
            f"@environments/{environment}/vars.yml",
            "-m",
            "debug",
            "-a",
            f"var={variable}",
        ],
        check=True,
        capture_output=True,
        cwd="deploy",
    )
    json_data = re.sub(r"^[^{]+", "", result.stdout.decode("utf-8"))
    value = json.loads(json_data)[variable]
    return value


def get_ssh_host_port(environment: str):
    inventory_data = load_inventory(environment)

    port = 22
    host = inventory_data["webservers"]["hosts"][0]

    return host, port


def run_playbook(
    environment: str,
    playbook_name: Path,
    username: str = None,
    extra_playbook_vars: dict = None,
):
    extra_playbook_vars = extra_playbook_vars or {}

    environment_dir = os.path.join("deploy", "environments", environment)
    inventory_file = os.path.abspath(os.path.join("deploy", "inventory", environment))
    playbook_file = os.path.abspath(os.path.join("deploy", "playbooks", playbook_name))
    vault_pass_file = os.path.abspath(".vault_pass")

    if not os.path.exists(environment_dir) or not os.path.exists(inventory_file):
        raise ValueError(f"Environment '{environment}' is invalid")

    if not playbook_file.endswith(".yml"):
        playbook_file = playbook_file + ".yml"

    if not os.path.exists(playbook_file):
        raise ValueError(f"Playbook '{playbook_name}' does not exist")

    if os.path.exists(vault_pass_file):
        st = os.stat(vault_pass_file)
        if oct(st.st_mode) != "0o100600":
            raise ValueError(f"Permissions of {vault_pass_file} should be 0600!")
        vault_args = ["--vault-password-file", vault_pass_file]
    else:
        vault_args = ["--ask-vault-pass"]

    if username is None:
        username = os.getlogin()

    extra_var_args = []
    for k, v in extra_playbook_vars.items():
        extra_var_args.append("-e")
        extra_var_args.append(f"{k}={v}")

    subprocess.run(
        ["ansible-playbook"]
        + vault_args
        + [
            "-i",
            inventory_file,
            "-e",
            "@environments/all/vars.yml",
            "-e",
            "@environments/all/devs.yml",
            "-e",
            f"@environments/{environment}/vars.yml",
            "-e",
            f"@environments/{environment}/secrets.yml",
            "-e",
            f"ansible_ssh_user={username}",
        ]
        + extra_var_args
        + [
            playbook_file,
        ],
        cwd="deploy",
    )
