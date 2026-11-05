---
name: kairos
description: Build, review, and debug Kairos System One API integrations for semantic classification, intent routing, scoring, and evidence checks. Use when writing Kairos questions, preparing state, interpreting structured answers, or identifying suitable Kairos workflows in an application.
---

# Build with Kairos

## Start every invocation with setup checks

Follow [the setup and update workflow](references/setup.md) before proceeding: run `scripts/check_setup.py` from this installed skill to check for a newer release and the presence of the exact environment variable `KAIROS_API_KEY`. Never reveal its value. If a newer version is available, ask whether to update automatically; on yes, execute the update using the existing installation method and scope, verify it, and reload the instructions. If the key is absent, guide the user to create a Kairos-group API key at `https://minara.cloud`, export it as `KAIROS_API_KEY`, and launch the agent from that environment. Planning can continue, but live requests require the key. Run the version check once per invocation, not once per API request.

## Build the integration

Use Kairos to turn application context into structured judgments. Keep the application's business decisions in code: Kairos provides evidence about language or images, while code applies permissions, arithmetic, thresholds, and actions.

This skill targets Kairos through the Minara gateway. Read [the API contract](references/api.md) before implementing requests. Read [workflow recipes](references/patterns.md) when choosing questions or designing routing and evaluation. Do not assume TypeSafe Jev features or SDKs are supported merely because the protocols resemble each other.

For news trading, read [the workflow guide](references/news-trading.md). Use `task_profile: general` for custom long/short/skip, factual judgments, or holding-period questions. For `news_return`, read [the fixed template workflow](references/news-return.md) and load `assets/news-return.json` from this skill. Its question and candidate IDs are fixed; interval descriptions must match the state as documented; fill the caller's required state fields into the template state. `/v1/news/templates` is not exposed to users: never call it or ask users to retrieve a template. Only the documented cross-field rule may change the candidate interval descriptions; preserve the question instructions and candidate IDs.

## Start with the application decision

Identify the output the application needs and the evidence it requires. Use ordinary code for exact lookups, calculations, account permissions, and explicit rules. Use Kairos for the parts that require interpreting content.

For open-ended requests, inspect the relevant application flow and propose a small number of concrete opportunities. Explain the additional network dependency and how to evaluate the benefit. For a concrete integration, implement it within the user's requested scope.

## Prepare state and questions

- Supply relevant source material, speaker roles, and domain definitions in structured state. A reader should be able to answer from the supplied evidence; do not assume live market data or external retrieval.
- Ask one observable question at a time. Separate independent labels into separate `noul` questions; use `choice` for mutually exclusive candidates and `score` for ordered, described levels.
- Include enough context to distinguish ambiguous cases. Truncate only with an explicit policy that preserves required evidence.
- Keep question wording, criteria, and decision thresholds together so they can be reviewed and versioned.
- Define the no-match path explicitly. A choice among candidates alone does not establish that any candidate applies; use a separate applicability judgment where needed.
- Bundle questions with shared state within deployment limits. Do not assume questions can see one another's answers. Make a later call when earlier results are needed to construct its input.

## Integrate the contract

Use `POST /v1/systemone` with a server-side API key and `model: DMIND/Kairos`. Let users configure `KAIROS_BASE_URL` and `KAIROS_API_KEY`; default the base URL to `https://minara.cloud` only when no override is supplied. The key is needed only for live API calls, not for installing the skill, planning, or generating code. Read it from the execution environment; do not ask users to paste it into chat or save it in skill files. Never provide a default API key. Normalize a trailing slash before appending the endpoint; the base URL excludes `/v1`. Use `DMIND/Kairos` exactly for all requests; model-list discovery is not required. Do not use Chat Completions, streaming, or legacy alpha paths. When constructing a request with image assets, automatically add `TypeSafe-Danger-Zone-Images: true`; do not ask the user to configure this header.

Validate returned answer IDs, types, finite numeric values, and option membership before using them. Preserve valid zero values. A missing answer or failed request is an error, not a negative judgment. Route uncertainty and failure to explicit application behavior.

If the key cannot access `DMIND/Kairos`, tell the user to check that the API key belongs to a Kairos-enabled group and that its model permissions allow the requested ID. Do not assume the `default` group includes Kairos or silently change the model, key, or group.

Use `noul` as a probability rather than a Boolean or severity score. Read `score` against its defined levels. Do not treat `confidence` as a measured accuracy guarantee or assume Jev's calibration transfers to Kairos. Choose thresholds using labeled examples and the consequences of errors, rather than copying universal cutoffs.

## Evaluate and debug

Start with representative inputs, ambiguous cases, negative cases, and cases where no candidate fits. Compare decisions against expected outcomes and reserve examples not used to tune the questions. Avoid assertions on exact floating-point probabilities.

Before a live experiment, establish authorization for the data and API requests, the configured endpoint, and a bounded request budget. Existing explicit authorization suffices. Keep keys out of source code and logs. Use synthetic fixtures when live calls are not authorized; distinguish protocol validation from measured model quality.

For an unexpected answer, inspect the actual payload, missing evidence, candidate coverage, and question scope before tweaking wording. For request failures, follow the error contract in the reference; bound retries and do not retry invalid input unchanged.

Report which checks used fixtures and which used the actual service. Do not claim latency, accuracy, or calibration improvements without measurements.

## Contract maintenance

The bundled reference combines gateway validation with the owner-provided API contract dated 2026-11-05. Updated upstream limits require confirmation of the Cloud rollout. When working in the source repository, consult that document and `docs/openapi/relay.json` for updates. For an installed standalone copy, consult the configured service's `/docs/system-one` documentation or obtain its current contract. Deployment-specific model capabilities need confirmation; do not invent a public hostname, SDK, version, or news template.
