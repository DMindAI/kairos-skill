# Workflow recipes

These are application design examples, not measured Kairos benchmarks. Use the general task profile unless a deployment-specific contract is explicitly required.

## Intent routing

Provide the message and relevant conversation context. Use a choice among clearly described handlers, and a separate noul to determine whether any supported handler applies when that distinction matters. Code handles unsupported or uncertain input and validates permissions before dispatch. Model classification alone does not authorize an action.

## Content or evidence checks

Supply the claim and the actual source passage. Ask separate questions about concrete evidence needed by the application. Define how contradictory, missing, or ambiguous evidence affects the outcome. A judgment based only on supplied text is not external fact verification.

## Candidate selection

Use deterministic extraction or retrieval to prepare candidates. Ask which candidate fits the user's intent, then copy the original candidate value in code. Include a no-match path. Stay within Kairos option and context limits; if reducing candidates first, measure whether that stage drops the correct answer.

## Composite scoring

Define ordered levels for each dimension and ask one score question per dimension. Combine scores with explicit weights in code. Keep weights and thresholds reviewable; evaluate the resulting decisions against labeled cases, including boundary cases. Check distributions when the average hides disagreement between distant levels.

## News workflows

For general news categorization, supply the article, timestamp, asset context, and explicit category definitions. Do not imply the model fetched current prices or knows events absent from state.

For custom long/short/skip, factual judgments, or model-selected holding periods, use `general`. Ask a separate `choice` question for a model-selected period; express a fixed period in state or instructions. For `news_return`, follow the [strict template workflow](news-return.md): load the bundled JSON locally, preserve its question and candidate IDs and validate interval descriptions against the state, and supply the caller's required state fields. Keep the seven-bin gross-return distribution separate from application trading decisions.

## Evaluation record

Record the question and criteria version, source fixture, expected application outcome, actual answer, final application outcome, latency, usage, and available model version metadata. Keep credentials and private data out of shared reports. Use held-out cases to check changes and report model errors separately from transport/schema errors. A simulated response verifies integration behavior only.
