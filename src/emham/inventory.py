import json
import os
import subprocess


def load_inventory(environment: str):
    inventory_file = os.path.abspath(os.path.join("deploy", "inventory", environment))
    results = subprocess.run(
        [
            "ansible-inventory",
            "-i",
            inventory_file,
            "--list",
        ],
        capture_output=True,
        check=True,
    )
    return json.loads(results.stdout)
