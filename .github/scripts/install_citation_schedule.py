#!/usr/bin/env python3
"""Install a local macOS citation update task for 09:00 each day."""

import os
from pathlib import Path
import plistlib
import shutil
import subprocess
import sys


LABEL = "org.xiuyue.citations"


def main():
    if sys.platform != "darwin":
        raise SystemExit("This installer requires macOS launchd.")

    state = Path.home() / "Library/Application Support/xiuyue-citations"
    state.mkdir(parents=True, exist_ok=True, mode=0o700)
    runner = state / "run.sh"
    shutil.copyfile(Path(__file__).with_name("run_citation_update.sh"), runner)
    runner.chmod(0o700)

    venv = state / "venv"
    python = venv / "bin/python"
    if not python.is_file():
        subprocess.run([sys.executable, "-m", "venv", str(venv)], check=True)
    subprocess.run(
        [str(python), "-m", "pip", "install", "beautifulsoup4>=4.12,<5"],
        check=True,
    )

    agents = Path.home() / "Library/LaunchAgents"
    agents.mkdir(parents=True, exist_ok=True)
    plist_path = agents / f"{LABEL}.plist"
    configuration = {
        "Label": LABEL,
        "ProgramArguments": ["/bin/bash", str(runner)],
        "WorkingDirectory": str(state),
        "EnvironmentVariables": {
            "PATH": "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin",
            "TZ": "Asia/Shanghai",
        },
        # launchd calendar times use the Mac's configured system time zone.
        "StartCalendarInterval": {"Hour": 9, "Minute": 0},
        "RunAtLoad": True,
        "StandardOutPath": str(state / "update.log"),
        "StandardErrorPath": str(state / "update.log"),
    }
    with plist_path.open("wb") as output:
        plistlib.dump(configuration, output)
    plist_path.chmod(0o600)

    domain = f"gui/{os.getuid()}"
    subprocess.run(
        ["launchctl", "bootout", f"{domain}/{LABEL}"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    subprocess.run(["launchctl", "bootstrap", domain, str(plist_path)], check=True)
    print(f"Installed {LABEL}: daily at 09:00 in the Mac's system time zone, plus login/load.")
    print(f"Task started. Log: {state / 'update.log'}")
    print(f"LaunchAgent: {plist_path}")


if __name__ == "__main__":
    main()
