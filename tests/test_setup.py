"""Offline checks for version comparison and secret-free setup reporting."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_setup", ROOT / "skills/kairos/scripts/check_setup.py"
)
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class SetupChecks(unittest.TestCase):
    def test_numeric_version_comparison(self):
        for latest, expected in [("0.1.10", "update_available"), ("0.1.4", "current"), ("0.1.3", "ahead")]:
            with self.subTest(latest=latest):
                payload = json.dumps({"name": "kairos", "version": latest}).encode()
                with patch.object(setup.Path, "read_text", return_value='{"version":"0.1.4"}'), patch.object(setup.urllib.request, "urlopen", return_value=io.BytesIO(payload)):
                    result = setup.check_version()
                self.assertEqual(result["status"], expected)

    def test_unavailable_release_is_unknown(self):
        with patch.object(setup.urllib.request, "urlopen", side_effect=TimeoutError), patch.object(setup.subprocess, "run", side_effect=FileNotFoundError):
            result = setup.check_version()
        self.assertEqual(result["status"], "unknown")

    def test_invalid_release_is_unknown(self):
        for payload in [b"not-json", b"[]", b'{"name":"other","version":"9.0.0"}', b'{"name":"kairos","version":"next"}']:
            with self.subTest(payload=payload):
                with patch.object(setup.urllib.request, "urlopen", return_value=io.BytesIO(payload)):
                    self.assertEqual(setup.check_version()["status"], "unknown")

    def test_key_presence_does_not_disclose_secret_or_accept_other_names(self):
        for env, configured in [({}, False), ({"KAIROS_API_KEY": "  "}, False), ({"OPENAI_API_KEY": "sentinel-secret"}, False), ({"KAIROS_API_KEY": "sentinel-secret"}, True)]:
            with self.subTest(configured=configured):
                output = io.StringIO()
                with patch.dict(setup.os.environ, env, clear=True), patch.object(setup, "scheduled_version_check", return_value={"status": "unknown"}), contextlib.redirect_stdout(output):
                    setup.main([])
                self.assertEqual(json.loads(output.getvalue())["api_key"]["configured"], configured)
                self.assertNotIn("sentinel-secret", output.getvalue())

    def test_version_request_does_not_send_api_key(self):
        payload = b'{"name":"kairos","version":"0.1.4"}'
        with patch.dict(setup.os.environ, {"KAIROS_API_KEY": "sentinel-secret"}), patch.object(setup.urllib.request, "urlopen", return_value=io.BytesIO(payload)) as fetch:
            setup.check_version()
        request = fetch.call_args.args[0]
        self.assertNotIn("sentinel-secret", request.full_url + str(request.headers))
        self.assertFalse(request.has_header("Authorization"))

    def test_private_repository_fallback_uses_existing_git_access_without_api_key(self):
        payload = b'{"name":"kairos","version":"0.1.10"}'
        completed = setup.subprocess.CompletedProcess([], 0, stdout=payload)
        with patch.object(setup.urllib.request, "urlopen", side_effect=OSError), patch.dict(setup.os.environ, {"KAIROS_API_KEY": "sentinel-secret"}), patch.object(setup.subprocess, "run", return_value=completed) as git:
            result = setup.check_version()
        self.assertEqual(result["status"], "update_available")
        self.assertEqual(result["transport"], "git-ssh")
        self.assertEqual(git.call_count, 2)
        for call in git.call_args_list:
            self.assertNotIn("KAIROS_API_KEY", call.kwargs["env"])
            self.assertEqual(call.kwargs["env"]["GIT_TERMINAL_PROMPT"], "0")

    def test_update_attempts_are_throttled_including_failures(self):
        for status in ["unknown", "current", "update_available"]:
            with self.subTest(status=status), tempfile.TemporaryDirectory() as directory:
                cache = Path(directory) / "check.json"
                with patch.object(setup, "check_version", return_value={"status": status}) as check:
                    with patch.object(setup.time, "time", return_value=100000):
                        self.assertEqual(setup.scheduled_version_check(cache_path=cache)["status"], status)
                        self.assertEqual(setup.scheduled_version_check(cache_path=cache)["status"], "skipped")
                    check.assert_called_once()
                    with patch.object(setup.time, "time", return_value=186400):
                        setup.scheduled_version_check(cache_path=cache)
                    self.assertEqual(check.call_count, 2)

    def test_force_check_bypasses_throttle(self):
        with tempfile.TemporaryDirectory() as directory:
            cache = Path(directory) / "check.json"
            with patch.object(setup, "check_version", return_value={"status": "current"}) as check:
                setup.scheduled_version_check(cache_path=cache)
                setup.scheduled_version_check(force=True, cache_path=cache)
            self.assertEqual(check.call_count, 2)

    def test_release_versions_match(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
        skill = json.loads((ROOT / "skills/kairos/version.json").read_text())
        self.assertEqual(plugin["version"], skill["version"])


if __name__ == "__main__":
    unittest.main()
