# News return API profile

Use `task_profile: news_return` with `POST /v1/systemone` and `model: DMIND/Kairos`. Load the [bundled template](../assets/news-return.json) locally and deep-copy `example` as the request body. Template metadata (`horizons`, `objective`, `candidate_order`) is not part of the request. Never call `/v1/news/templates`; it is not exposed through this integration.

## Required state

The state object must contain exactly these 12 fields. Replace example values with actual caller inputs.

| Field | Input requirement |
| --- | --- |
| `news_text` | News text |
| `target_asset` | Target asset identifier |
| `market` | Market identifier |
| `asset_class` | Asset category |
| `event_type` | Event category |
| `source_name` | News source |
| `published_at_utc` | Publication timestamp; UTC ISO 8601 recommended |
| `horizon` | Exactly `15m`, `1h`, or `4h` |
| `entry_rule` | Entry timestamp, price selection, and session rules |
| `round_trip_cost_bp` | Required positive finite number; controls the interval boundaries below |
| `availability_basis` | Basis for when the input became available |
| `return_objective` | Output definition, consistent with the template's gross-return objective |

## Question validation

Preserve the question ID `return_distribution`, type `choice`, instructions, and ordered candidate IDs `return_bin_0` through `return_bin_6`. The numeric boundaries in candidate descriptions must match `state.round_trip_cost_bp`; the bundled numbers are an example, not constant boundaries.

Let `c = state.round_trip_cost_bp`. Construct boundaries `[-4*c, -2*c, -c, c, 2*c, 4*c]`. For each candidate use the exact description format `Gross asset return in [LOWER, UPPER) bp.`. The first lower bound is `-infinity`; the final upper bound is `+infinity`. Format finite bounds consistently, without unnecessary trailing zeros. For example, an input value of 10 requires boundaries -40, -20, -10, 10, 20, 40.

Update these descriptions whenever that input changes. Do not change the question instructions, rename candidates, add questions, or supply arbitrary boundaries. Other intervals or horizons require `task_profile: general`.

Use a separate request for each caller-selected horizon. Submit using the configured base URL and API key. Some example strings use JSON Unicode escapes; parse normally without double-escaping.

## Response validation

Read `answers.return_distribution.probabilities` in the template's `candidate_order`. Require all seven IDs, finite values in [0, 1], and a sum close to 1 with floating-point tolerance. Preserve valid zeros; do not silently normalize malformed responses.

Return the complete distribution with its actual interval descriptions and horizon. The API does not automatically return additional answers or a representative value for each interval. If the service rejects the template, report the error and check for a skill update; do not silently switch profiles.

Contract source: owner-provided API documentation dated 2026-11-05, with the owner-specified Cloud model alias and local template distribution. No live forecast was performed.
