# Fixed news return template

Read this reference before implementing `news_return_v4`. The [bundled JSON](../assets/news-return-v4.json) preserves the deployment template supplied by the project owner on 2026-11-04. It is not a live API response fetched during skill creation, a prediction result, or a current news feed.

The project owner confirmed on 2026-11-04 that this supplied JSON is the authoritative news contract and the public News profile page is awaiting correction. Read [the contract differences](news-trading.md) to avoid importing the website's seven-field schema or bin IDs. Preserve all 12 state fields in this template.

## Build a request

1. Load the JSON and deep-copy its `example` object as the request body. The surrounding `horizons`, `objective`, and `candidate_order` are template metadata, not request fields.
2. Use the account's configured gateway model ID. The supplied template's `kairos` identifies its example model; the gateway documentation uses `Dmind/Kairos`. Neither name proves account access. Model selection does not change the task template.
3. Populate the state with the actual news, target asset, market, asset class, event type, source, publication timestamp, and availability basis. Keep the provided field names and do not infer undocumented enum values from the example. Do not reuse CRCL, the historical timestamp, or historical availability wording as defaults for unrelated news.
4. Require the caller to choose `state.horizon` from `15m`, `1h`, or `4h`. Do not choose a horizon based on the model's output. A request has one shared horizon; use separate requests for explicitly requested multiple horizons.
5. Keep `task_profile: news_return_v4`, the question ID `return_distribution`, question type, instructions, seven candidate IDs, candidate order, and criteria exactly as supplied. Do not translate or paraphrase the fixed question or add generic choice questions as a substitute.

The request is submitted through the same configurable gateway `/v1/systemone` endpoint described in [the API reference](api.md). Loading this bundled template does not need an upstream key or a call to `/v1/news/templates`.

## Return semantics

The question forecasts the target asset's **gross**, unadjusted open-to-open return in basis points over the supplied horizon. It does not output a trade, position size, net return, or holding-period recommendation.

The supplied template specifies a 15 bp round-trip cost separately and these seven intervals:

| Candidate | Gross return interval (bp) |
| --- | --- |
| `return_bin_0` | `[-infinity, -60)` |
| `return_bin_1` | `[-60, -30)` |
| `return_bin_2` | `[-30, -15)` |
| `return_bin_3` | `[-15, 15)` |
| `return_bin_4` | `[15, 30)` |
| `return_bin_5` | `[30, 60)` |
| `return_bin_6` | `[60, +infinity)` |

Although the metadata calls these cost-scaled bins, this supplied artifact defines only the 15 bp example. It does not specify how to construct templates for other costs. Preserve the 15 bp cost and its matching bins when using this template. If the caller needs a different cost, obtain that deployment's supported template or scaling contract; do not silently substitute 15 bp or invent rescaled boundaries.

The entry rule uses the first minute-bar open at or after publication plus 60 seconds. For stocks, entry and exit must be in the same regular exchange session. Preserve this rule when using the supplied template. Application code must check timing/session eligibility using suitable market data; the prediction is not proof that a trade was executable.

## Read the result

Read `answers.return_distribution.probabilities` by the seven fixed IDs in `candidate_order`. Validate completeness, finite values in [0, 1], and a distribution sum close to 1 with a numerical tolerance. Surface invalid distributions as errors rather than silently filling or renormalizing them. Preserve legitimate zeros.

Present the full distribution with the asset, caller-selected horizon, and gross-return units. A selected bin is not a guaranteed outcome. Do not derive an exact expected return from bin midpoints: the tail intervals are unbounded and the within-bin distribution is unspecified. Any trading policy belongs in application code and requires its own assumptions and evaluation.
