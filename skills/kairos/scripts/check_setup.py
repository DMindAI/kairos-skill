#!/usr/bin/env python3
"""Report installed version, available updates, and API key presence without secrets."""

import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import urllib.request


RELEASE_URL = (
    "https://raw.githubusercontent.com/DMindAI/kairos-skill/"
    "main/.claude-plugin/plugin.json"
)


def version_tuple(value):
    if not isinstance(value, str) or not re.fullmatch(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", value):
        raise ValueError("Expected a stable major.minor.patch version")
    return tuple(int(part) for part in value.split("."))


def release_content():
    try:
        request = urllib.request.Request(RELEASE_URL, headers={"Accept": "application/json"})
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.read(65537), "https"
    except OSError:
        # Private repositories may be installable over SSH but unavailable over public HTTP.
        env = os.environ.copy()
        env.pop("KAIROS_API_KEY", None)
        env["GIT_TERMINAL_PROMPT"] = "0"
        env["GIT_SSH_COMMAND"] = "ssh -o BatchMode=yes -o ConnectTimeout=5"
        with tempfile.TemporaryDirectory(prefix="kairos-version-") as directory:
            subprocess.run(
                ["git", "clone", "--quiet", "--depth=1", "--single-branch", "--branch=main",
                 "--no-checkout", "git@github.com:DMindAI/kairos-skill.git", directory],
                env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                timeout=20, check=True,
            )
            result = subprocess.run(
                ["git", "-C", directory, "show", "HEAD:.claude-plugin/plugin.json"],
                env=env, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                timeout=5, check=True,
            )
            return result.stdout, "git-ssh"


def check_version():
    result = {"status": "unknown", "source": RELEASE_URL}
    try:
        local = json.loads(
            (Path(__file__).resolve().parents[1] / "version.json").read_text()
        )["version"]
        local_parts = version_tuple(local)
        result["installed"] = local
    except (OSError, ValueError, KeyError, TypeError):
        result["reason"] = "Cannot read a valid installed version"
        return result

    try:
        content, transport = release_content()
        result["transport"] = transport
        if len(content) > 65536:
            raise ValueError("Release metadata exceeds size limit")
        manifest = json.loads(content)
        if manifest.get("name") != "kairos":
            raise ValueError("Unexpected plugin name")
        latest = manifest["version"]
        latest_parts = version_tuple(latest)
        result["latest"] = latest
        result["status"] = (
            "update_available" if latest_parts > local_parts
            else "current" if latest_parts == local_parts
            else "ahead"
        )
    except (OSError, ValueError, KeyError, TypeError, AttributeError, subprocess.SubprocessError):
        result["reason"] = "Release metadata unavailable or invalid; update status is unknown"
    return result


def main():
    print(json.dumps({
        "api_key": {
            "variable": "KAIROS_API_KEY",
            "configured": bool(os.environ.get("KAIROS_API_KEY", "").strip()),
        },
        "version": check_version(),
    }))


if __name__ == "__main__":
    main()
