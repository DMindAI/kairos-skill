#!/usr/bin/env python3
"""Report installed version, available updates, and API key presence without secrets."""

import argparse
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
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


def scheduled_version_check(force=False, cache_path=None):
    cache_path = cache_path or Path(
        os.environ.get("XDG_CACHE_HOME") or Path.home() / ".cache"
    ) / "kairos-skill" / "update-check.json"
    now = time.time()
    if not force:
        try:
            checked_at = json.loads(cache_path.read_text())["checked_at"]
            if isinstance(checked_at, (int, float)) and 0 <= now - checked_at < 86400:
                return {"status": "skipped", "reason": "Already checked within 24 hours"}
        except (OSError, ValueError, KeyError, TypeError):
            pass
    # Record attempts, including failures, to avoid repeated network delays.
    try:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w", dir=cache_path.parent, delete=False) as cache:
            temporary = Path(cache.name)
            json.dump({"checked_at": now}, cache)
        temporary.replace(cache_path)
    except OSError:
        # Without persistent state, automatic checks cannot be throttled reliably.
        if not force:
            return {"status": "skipped", "reason": "Update cache unavailable; use --force-update-check explicitly"}
    return check_version()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force-update-check", action="store_true")
    args = parser.parse_args(argv)
    print(json.dumps({
        "api_key": {
            "variable": "KAIROS_API_KEY",
            "configured": bool(os.environ.get("KAIROS_API_KEY", "").strip()),
        },
        "version": scheduled_version_check(force=args.force_update_check),
    }))


if __name__ == "__main__":
    main()
