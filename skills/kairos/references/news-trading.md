# News trading: choose the workflow

Official documentation reviewed on 2026-11-04:

- [News Trading use case](https://dmind.ai/docs/kairos/use-cases/trading): plain `general` questions for direction and a possible holding window.
- [News profile API](https://dmind.ai/docs/kairos/api-reference/news): news-profile background; use this skill's bundled contract where website examples differ.
- [Read the signal](https://dmind.ai/docs/kairos/guides/news-decisions): distributions, side aggregation, and horizon selection.
- [Validate a workflow](https://dmind.ai/docs/kairos/guides/news-workflow): news ingestion, replay, and forward paper evaluation.

## General news judgments

Use `task_profile: general` for custom long/short/skip, factual judgments, or holding-period questions. Define business-specific action choices explicitly; the application remains responsible for permissions and execution. To request a model-selected holding period, add a `choice` question in `questions`. If the period is fixed by the caller, put it in `state` or `instructions`.

The use-case page's direction and holding-window examples are ordinary general questions. A `24h` choice in a general example does not extend the supported horizons of the compatibility news profile. Kairos evaluates the supplied news; the application supplies the feed and maps the target asset.

## Strict return distributions

Use `news_return_v4` for the existing seven-bin gross-return task. Follow [the fixed template workflow](news-return-v4.md): load the bundled JSON locally, supply the asset, news, caller-selected `15m`/`1h`/`4h` horizon, cost, and entry rule, and preserve its strict question and candidates. The template endpoint is not exposed to users and must not be called.

The owner's bundled template defines the 12 state fields and `return_bin_0` through `return_bin_6`. Do not mix in website examples with seven state fields and `bin_0` keys. Do not replace the fixed template with a general question. Return the distribution and let the application strategy determine trading actions.

## Interpret and evaluate

Use the bundled template's ordered candidates: add the first three probabilities for falling, use the middle probability for flat, and add the last three for rising. Reference the actual candidate IDs rather than assuming the website's names. This aggregation retains more information than selecting the single largest bin. Keep the full distribution and interval descriptions available.

A trading rule can compare these side probabilities, require a minimum gap, or skip uncertain results. The documentation's numerical thresholds are illustrations, not validated defaults for a new application. Choose thresholds on one period and evaluate on a later period. A weighted midpoint summary requires explicit assumptions for unbounded tails and is not an exact expected return.

Map assets by market as well as symbol, preserve the source publication time, record actual receipt and processing times, and handle stale items explicitly. Feed ingestion, deduplication, prices, position sizing, costs, and execution belong to the application. Evaluate net results and a market-relative benchmark separately from the model's gross-return prediction.

Distinguish the site's later API calls on historical headlines from its historical replays and forward paper results. None is a live result produced by installing or validating this skill. Use the caller's entry rules and the bundled template's return-window contract when evaluating predictions against execution P&L.
