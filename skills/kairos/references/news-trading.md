# News trading: choose the workflow

Official documentation reviewed on 2026-11-04:

- [News Trading use case](https://dmind.ai/docs/kairos/use-cases/trading): plain `general` questions for direction and a possible holding window.
- [News profile API](https://dmind.ai/docs/kairos/api-reference/news): registered `news_return_v4` questions and template retrieval.
- [Read the signal](https://dmind.ai/docs/kairos/guides/news-decisions): distributions, side aggregation, and horizon selection.
- [Validate a workflow](https://dmind.ai/docs/kairos/guides/news-workflow): news ingestion, replay, and forward paper evaluation.

## General news judgments

The use-case page calls `/v1/systemone` with model `kairos` and `task_profile: general`. Its custom choices ask about price direction (`rise`, `flat`, `fall`) and separately about a likely holding window. These are ordinary configurable questions, not the registered news template. Some general examples include a `24h` option; that does not extend the fixed news profile's supported horizons.

Kairos evaluates the supplied item. The application supplies the news feed, maps the target asset, and applies its own decision rule. A directional answer alone does not quantify return size or establish that fees are covered. A model-selected window from a general question is not the caller-specified horizon of `news_return_v4`.

## Fixed return distributions

For the user's requested fixed-template integration, retain the [owner-supplied JSON](../assets/news-return-v4.json) and read [its workflow](news-return-v4.md). Do not replace it with the general demo or edit its registered question to match website examples.

The project owner confirmed on 2026-11-04 that the supplied JSON is authoritative and the public News profile page is awaiting correction. The differences are recorded here to prevent accidental schema mixing:

| Contract item | Owner-supplied artifact | Public News profile page |
| --- | --- | --- |
| State | 12 fields, including cost, source, entry rule and availability | Exactly 7 fields: news, asset, market, asset class, event type, publication time and horizon |
| Candidate IDs | `return_bin_0` through `return_bin_6` | `bin_0` through `bin_6` |
| Bin definitions | Supplied 15 bp cost example | Selected by market, asset class and horizon |
| Return window | Open-to-open with supplied entry rule | Described relative to source publication |
| Template retrieval | Repository gateway documentation describes an upstream-only endpoint | Public docs advertise authenticated Cloud `GET /v1/news/templates` |

These are not interchangeable schemas. Use the owner-supplied artifact unchanged: preserve its 12 state fields, return_bin_0 through return_bin_6, and matching cost/entry conventions. Do not remove fields, rename bins, or rescale intervals to match the website. The template is bundled, so no retrieval is required; neither retrieval path was live-tested during this work. Treat a future template revision as a contract update requiring verified deployment evidence, not a reason to silently rewrite this artifact.

## Interpret and evaluate

Use the verified template's ordered candidates: add the first three probabilities for falling, use the middle probability for flat, and add the last three for rising. Reference the actual candidate IDs rather than assuming the website's names. This aggregation retains more information than selecting the single largest bin. Keep the full distribution and interval descriptions available.

A trading rule can compare these side probabilities, require a minimum gap, or skip uncertain results. The documentation's numerical thresholds are illustrations, not validated defaults for a new application. Choose thresholds on one period and evaluate on a later period. A weighted midpoint summary requires explicit assumptions for unbounded tails and is not an exact expected return.

Map assets by market as well as symbol, preserve the source publication time, record actual receipt and processing times, and handle stale items explicitly. Feed ingestion, deduplication, prices, position sizing, costs, and execution belong to the application. Evaluate net results and a market-relative benchmark separately from the model's gross-return prediction.

Distinguish the site's later API calls on historical headlines from its historical replays and forward paper results. None is a live result produced by installing or validating this skill. Use the supplied artifact's entry and return-window rules when evaluating its predictions against execution P&L; do not substitute the website's publication-relative wording.
