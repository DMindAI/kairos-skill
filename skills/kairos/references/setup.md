# Invocation checks and updates

## Check once at the start of each invocation

Run the bundled helper from the installed skill directory, resolving the absolute path from the skill you loaded:

```bash
python3 /absolute/path/to/kairos/scripts/check_setup.py
```

The helper checks only whether `KAIROS_API_KEY` is non-empty; it never prints the key or sends it to GitHub. It reads the local `version.json` and compares stable numeric versions with the plugin manifest on the repository's `main` branch. It does not call the model, install anything, or modify configuration. A present key is not proof of validity or group access.

If public GitHub HTTP access fails, the helper tries a temporary shallow SSH clone using existing Git credentials, without interactive authentication or the Kairos key in the subprocess environment. It reads only the release manifest and cleans up the temporary checkout. This supports private repositories when the user already has SSH access; no Git credentials are created or changed. If neither method works, the result is unknown. A preview feature branch is not the release source: new releases become discoverable after they land on `main`.

If Python is unavailable, read `version.json` and the same remote manifest using available file/HTTP tools and check environment-variable presence without revealing its value. If a check cannot run, say which result is unknown; do not claim the installation is current or the key is missing. Do not install a runtime just to perform the check.

## Offer and perform an update

For `update_available`, show the installed and latest versions and ask one yes/no question: "Kairos skill X is installed; Y is available. Update automatically now?"

- **Yes:** perform the update yourself with the existing installation method and scope. Do not ask again or merely hand the user commands. This authorizes this update, not every future release.
- **No:** continue with the installed version; do not ask again during the same invocation.
- **No answer:** do not update. Continue independent work with the installed version while the question remains pending.
- **Current or ahead:** no update prompt; never downgrade a preview checkout to an older release.
- **Unknown:** report the check limitation briefly and continue. A timeout, 404, or malformed response is not evidence that no update exists.

Determine the installation method from the loaded skill path and available installer metadata. Do not create a second copy in another agent or change project/global scope.

For the Claude Code plugin, run in sequence and stop on failure:

```bash
claude plugin marketplace update dmind-ai
claude plugin update kairos@dmind-ai
```

For a skills CLI installation, reinstall only this skill for the same agent and scope:

```bash
npx --yes skills add DMindAI/kairos-skill --skill kairos --agent <installed-agent> --yes
```

Add `--global` only if the existing installation is global. Resolve `<installed-agent>` from the installation, such as `codex` or `claude-code`; it is not a literal command argument. Do not run a blanket update of unrelated skills.

For a manual installation, retrieve the repository at the checked release commit and replace only the installed Kairos directory. Preserve a backup and do not overwrite local modifications without resolving their intended treatment. If the installation method is ambiguous or an updater fails, explain the specific obstacle rather than guessing or claiming success.

After updating, locate the active installation again and verify its local `version.json` against the expected release (or a newer version that became available meanwhile). Re-read its `SKILL.md` before continuing. If Claude Code still has the old plugin loaded, tell the user to run `/reload-plugins` or restart; distinguish files updated from the active session reloaded. Do not restart the user's session automatically.

## Missing API key

Accept only the exact environment variable `KAIROS_API_KEY`. Do not silently substitute `TYPESAFE_API_KEY`, `OPENAI_API_KEY`, or an agent-provider key.

If it is missing or blank, give these instructions:

1. Open [Minara Cloud](https://minara.cloud), sign in, and create an API key assigned to the **Kairos group**. If that group is not available, request Kairos access from the service administrator. A key in `default` may not have access to `DMIND/Kairos`.
2. Export the key in the terminal used to launch the agent:

```bash
export KAIROS_API_KEY="<your Kairos-group API key>"
```

3. Start or restart the agent from that terminal so its process inherits the variable. Exporting in a different terminal does not update an already-running agent. `KAIROS_BASE_URL` is optional and defaults to `https://minara.cloud`.
4. Invoke the skill again. Recheck presence without echoing the key. Do not ask the user to paste the secret into chat or write it into this repository.

Give the setup guide when the check fails even if the current task is planning or code generation; those tasks may continue without the key. Live calls must wait for configuration. Before a later live call in the same invocation, recheck if the user says they have configured the variable. No presence check can verify model permissions; keep the Kairos-group error guidance in the API reference.
