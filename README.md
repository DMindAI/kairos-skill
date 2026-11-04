# Kairos agent skill

Teach Claude Code, Codex, and other skill-aware coding agents to integrate Kairos through the Minara Cloud System One API. Includes typed question design, request and response contracts, image limits, error handling, and the strict `news_return_v4` template workflow.

## Install

Choose one installation method to avoid duplicate copies. The commands below install from the default branch.

### Claude Code

Run these two commands in your terminal:

```bash
claude plugin marketplace add DMindAI/kairos-skill
claude plugin install kairos@dmind-ai
```

Invoke `/kairos:kairos` in Claude Code, or ask it to “use the Kairos skill”.

### Codex and other agents

Run the skills installer and choose your agent when prompted:

```bash
npx skills add DMindAI/kairos-skill --skill kairos
```

Installation is project-local by default; add `-g` for a global installation. This command uses the `skills` installer from npm to install Kairos from GitHub; there is no separate Kairos npm package to install.

### Manual installation

Copy the entire `skills/kairos` directory into your agent's skill directory, including `references/` and `assets/`. For example, use `.claude/skills/kairos` for a project-local Claude Code installation or `~/.codex/skills/kairos` for a personal Codex installation. Read [SKILL.md](skills/kairos/SKILL.md) directly to inspect the instructions before installing.

## Update

For the Claude Code plugin:

```bash
claude plugin marketplace update dmind-ai
claude plugin update kairos@dmind-ai
```

Restart Claude Code or run `/reload-plugins` to load the update. For skills CLI installations, run `npx skills update`. For manual installations, replace the complete skill directory. Plugin releases must increment the version in `.claude-plugin/plugin.json` so users receive the new version.

## Configure

- `KAIROS_API_KEY`: your Minara Cloud API key, required only for live API calls. Keep it in your server environment or secret manager.
- `KAIROS_BASE_URL`: optional gateway origin, defaults to `https://minara.cloud`. Exclude `/v1` and the endpoint path.
- Model: use a model ID available to your account. Use the exact ID returned by authenticated `GET /v1/models`, preserving capitalization; do not assume `DMIND/Kairos` and `Dmind/Kairos` are interchangeable. The older gateway example uses `Dmind/Kairos`; the upstream news template preserves its supplied example name `kairos`.
- API key group: use a key assigned to a Kairos-enabled group. A key in `default` is not guaranteed to have access to `Dmind/Kairos`; also check key-level model restrictions.

The public endpoint is `POST /v1/systemone`, non-streaming. Installing this skill does not initiate API calls or configure credentials. Planning and code generation do not require a key. For live calls, supply the key through the environment inherited by the agent or backend; do not paste it into chat or store it in this repository.

## Use

Ask your agent:

> Use the Kairos skill to add structured intent routing to this application. Keep routing rules in code and handle unsupported requests explicitly.

> Use the Kairos skill to integrate news_return_v4 with a caller-selected 1h horizon. Load the fixed template bundled with the skill and return the full gross-return distribution.

> Use the Kairos skill to review our System One requests, error handling, and question design.

The compatibility profile `news_return_v4` supports `15m`, `1h`, and `4h`. Load `skills/kairos/assets/news-return-v4.json` locally, preserve its question and candidates, and supply the actual asset, news, horizon, cost, and entry rule. It predicts a gross-return distribution, not a trade action. See the [news reference](skills/kairos/references/news-return-v4.md) for fixed fields and input requirements.

## Troubleshooting

- **No access to `Dmind/Kairos`:** check whether the API key belongs to a Kairos-enabled group and permits that model. Do not assume the account's `default` group provides access.

See [error handling](skills/kairos/references/api.md) for response formats and bounded retries. Documentation is in English; original template state values that require non-English text are represented with JSON Unicode escapes without changing their decoded values.

## Contents

- [Skill instructions](skills/kairos/SKILL.md)
- [API contract and curl example](skills/kairos/references/api.md)
- [Workflow recipes](skills/kairos/references/patterns.md)
- [News trading workflows](skills/kairos/references/news-trading.md)
- [Fixed news workflow](skills/kairos/references/news-return-v4.md)
- [Bundled fixed news template](skills/kairos/assets/news-return-v4.json)

The contract snapshot is based on Minara gateway documentation and request validation as of 2026-11-04. The news template was supplied by the project owner. Live endpoint behavior, account permissions, latency, and predictive performance have not been verified by this repository's initial documentation validation.

Use `general` for custom long/short/skip, factual judgments, or model-selected holding periods. For `news_return_v4`, use the bundled fixed JSON. `/v1/news/templates` is not exposed to users and must not be called.

## License

[MIT](LICENSE).
