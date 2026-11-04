# Fixed news return template

`task_profile: news_return` identifies the seven-bin gross-return task. The [bundled JSON](../assets/news-return.json) is the fixed template supplied by the project owner and shipped with this skill. Load it locally; `/v1/news/templates` is not exposed to users. Do not call that endpoint or ask users to obtain a template.

## Build a request

1. Parse the bundled JSON and deep-copy its `example` object as the request body. `horizons`, `objective`, and `candidate_order` are template metadata, not request fields.
2. Set `model` to `DMIND/Kairos` exactly and preserve `task_profile: news_return`. No model-list query is required.
3. Keep the template's 12 state field names. Supply the actual asset, news, market, asset class, event type, source, publication time, availability basis, holding period, cost, entry rule, and return objective. The latter fields must describe the intended evaluation accurately. Do not reuse the historical example's asset, timestamp, or availability wording for unrelated news.
4. Require a caller-selected horizon of `15m`, `1h`, or `4h`. Use separate requests when the caller explicitly wants multiple horizons. This profile does not ask the model to choose a horizon.
5. Preserve `questions.return_distribution` exactly: type, instructions, all seven `return_bin_0` through `return_bin_6` IDs, their order, and criteria. Do not translate, paraphrase, rename, or rescale them. Do not mix in website examples using seven state fields or `bin_0` keys.
6. Submit the body to `POST /v1/systemone` using the configured `KAIROS_BASE_URL` (default `https://minara.cloud`) and `KAIROS_API_KEY`. Only this prediction request needs credentials; loading the template is local. If model access is denied, check that the key belongs to a Kairos-enabled group and permits the requested model.

Some original example state values are stored as JSON Unicode escapes to keep repository text in English while preserving their exact decoded values. Parse the JSON normally; do not translate those values or double-escape them in the outgoing request. The fixed question and candidates remain unchanged.

## Fixed intervals and caller inputs

The bundled question defines these gross-return intervals in basis points:

| Candidate | Gross return interval (bp) |
| --- | --- |
| `return_bin_0` | `[-infinity, -60)` |
| `return_bin_1` | `[-60, -30)` |
| `return_bin_2` | `[-30, -15)` |
| `return_bin_3` | `[-15, 15)` |
| `return_bin_4` | `[15, 30)` |
| `return_bin_5` | `[30, 60)` |
| `return_bin_6` | `[60, +infinity)` |

The example uses a 15 bp round-trip cost and a particular entry rule. Cost and entry rule are caller-provided state, not universal defaults. Changing them does not authorize changing the fixed candidate intervals. Do not invent a cost-scaling formula from the template's descriptive metadata. The model returns gross returns; apply the caller's actual costs separately in business calculations.

## Read the result

Read `answers.return_distribution.probabilities` by the fixed candidate IDs in `candidate_order`. Validate completeness, finite values in [0, 1], and a sum close to 1 with a numerical tolerance. Preserve valid zeros and surface invalid distributions as errors rather than silently renormalizing them.

Show all seven intervals with the asset and caller-selected horizon. Trading actions, sizing, costs, and execution rules belong to the business strategy; the most likely interval is not a trading instruction. Exact expected return cannot be recovered from interval probabilities without assumptions about within-bin returns and unbounded tails.

If a deployment rejects the bundled template, report the error and check for a skill update. Do not invent a replacement, silently switch to `general`, or direct users to the unexposed template endpoint. Template changes are distributed by the skill maintainer through versioned skill updates.

## Validation status

The question and candidates supplied by the owner are preserved verbatim; the example model is set to the owner-specified gateway ID `DMIND/Kairos`. No live forecast was performed while authoring this skill. Keep fixture checks distinct from service validation.
