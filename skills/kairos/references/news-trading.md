# News request profiles

## General questions

Use `task_profile: general` for custom choices, factual judgments, or holding-period questions. To request a holding-period answer, add an explicit `choice` question. For a caller-fixed period, supply it in `state` or `instructions`. Each question is evaluated independently; it cannot read another answer from the same request.

## Registered distribution question

Use `task_profile: news_return` for the registered seven-candidate question. Follow [the request contract](news-return.md), including the exact state fields, allowed horizons, and cross-field interval validation. Load the bundled template locally; do not request the unexposed template endpoint.

Return the complete `answers.return_distribution` response. This skill documents request construction and response validation; it does not define trading strategies or execution rules.
