import subprocess
import sys
import time
from pathlib import Path


def install_roles() -> int:
    roles_dir = Path("deploy/roles")

    for path in roles_dir.iterdir():
        if path.is_symlink():
            print(
                "**************************************************************************"
            )
            print(
                "* At least one role is installed via symlink; skipping role installation *"
            )
            print(
                "**************************************************************************"
            )
            time.sleep(2)
            return 0

    results = subprocess.run(
        ["ansible-galaxy", "install", "-r", "requirements.yml"],
        cwd="deploy",
        capture_output=True,
        check=True,
    )
    stderr = results.stderr.decode("utf-8")
    if "WARNING" in stderr:
        print("Out of date packages:", file=sys.stderr)
        print("", file=sys.stderr)
        for line in stderr.splitlines():
            if "WARNING" in line:
                print(line, file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "Unless you have made local changes to the role, remove those directories",
            file=sys.stderr,
        )
        print("from ./deploy/roles and try again.", file=sys.stderr)
        return 1
    return 0
