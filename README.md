# Kairos agent skill

Teach Claude Code, Codex, and other skill-aware coding agents to integrate Kairos through the Minara Cloud System One API. Includes typed question design, request and response contracts, image limits, error handling, and the strict `news_return_v4` template workflow.

## Install

With the skills CLI, select your coding agent when prompted:

```bash
npx skills add DMindAI/kairos-skill --skill kairos
```

The command above installs from the default branch after the skill has been merged. To try the initial implementation branch before merge:

```bash
npx skills add https://github.com/DMindAI/kairos-skill/tree/codex/kairos-agent-skill --skill kairos
```

Alternatively, copy the entire `skills/kairos` directory into your agent's skill directory, including `references/` and `assets/`. For example, use `.claude/skills/kairos` for a project-local Claude Code installation or `~/.codex/skills/kairos` for a personal Codex installation. Choose one method to avoid duplicate copies.

## Configure

- `KAIROS_API_KEY`: your Minara Cloud API key, required. Keep it in your server environment or secret manager.
- `KAIROS_BASE_URL`: optional gateway origin, defaults to `https://minara.cloud`. Exclude `/v1` and the endpoint path.
- Model: use a model ID available to your account. The gateway example uses `Dmind/Kairos`; the upstream news template preserves its supplied example name `kairos`.

The public endpoint is `POST /v1/systemone`, non-streaming. Installing this skill does not initiate API calls or configure credentials.

## Use

Ask your agent:

> Use the Kairos skill to add structured intent routing to this application. Keep routing rules in code and handle unsupported requests explicitly.

> Use the Kairos skill to integrate news_return_v4 with a caller-selected 1h horizon. Fetch the strict template from the configured service and return the full gross-return distribution.

> Use the Kairos skill to review our System One requests, error handling, and question design.

The compatibility profile `news_return_v4` supports `15m`, `1h`, and `4h`. Fetch `/v1/news/templates`, preserve its question and candidates, and supply the actual asset, news, horizon, cost, and entry rule. It predicts a gross-return distribution, not a trade action. See the [news reference](skills/kairos/references/news-return-v4.md) for fixed fields and input requirements.

## Contents

- [Skill instructions](skills/kairos/SKILL.md)
- [API contract and curl example](skills/kairos/references/api.md)
- [Workflow recipes](skills/kairos/references/patterns.md)
- [News trading workflows](skills/kairos/references/news-trading.md)
- [Fixed news workflow](skills/kairos/references/news-return-v4.md)
- [Owner-supplied template snapshot](skills/kairos/assets/news-return-v4.json)

The contract snapshot is based on Minara gateway documentation and request validation as of 2026-11-04. The news template was supplied by the project owner. Live endpoint behavior, account permissions, latency, and predictive performance have not been verified by this repository's initial documentation validation.

Use `general` for custom long/short/skip, factual judgments, or model-selected holding periods. The latest owner clarification requires the service-returned strict template for `news_return_v4`; the bundled JSON is an offline snapshot, not a replacement for template retrieval.

## License

[MIT](LICENSE).
