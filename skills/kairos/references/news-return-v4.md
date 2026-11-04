# Strict news return template workflow

`task_profile: news_return_v4` is the unchanged compatibility identifier for the existing return-bin task. This workflow follows the project owner's latest contract clarification on 2026-11-04.

## Retrieve the template

Fetch the template from the configured service before building the integration. Both the origin and key are user-configurable; the origin defaults to `https://minara.cloud` and excludes `/v1`.

```bash
: "${KAIROS_API_KEY:?Set KAIROS_API_KEY before fetching the template}"
KAIROS_BASE_URL="${KAIROS_BASE_URL:-https://minara.cloud}"
KAIROS_BASE_URL="${KAIROS_BASE_URL%/}"
curl --fail-with-body --max-time 30 "$KAIROS_BASE_URL/v1/news/templates" \
  -H "Authorization: Bearer $KAIROS_API_KEY"
```

Keep the successful JSON response as a reusable local template with its source origin and retrieval date. Never store the API key alongside it. Reuse the validated template for requests to that deployment; fetching it does not need to be repeated for every news item. Refresh it when the deployment contract changes or a template mismatch is reported. Do not silently use a cached template from a different service.

The [bundled owner-supplied JSON](../assets/news-return-v4.json) is an illustrative snapshot, preserved verbatim. It is useful for offline inspection and fixtures, but does not replace retrieving the configured service's strict template. A failed retrieval must surface as a setup error, not trigger invented question text or a silent switch to `general`.

## Build a request

1. Inspect the returned template and its input requirements. If it contains an `example` request, copy that request, not the enclosing metadata, as the starting body. Do not assume every deployment's template response has an identical wrapper.
2. Set `model` to the model ID available to the account and preserve `task_profile: news_return_v4`.
3. Supply the actual asset, news, holding period, cost, and entry rule in the fields required by the returned template. Fill any other required context accurately. Do not reuse the snapshot's historical news, 15 bp cost, or entry rule as universal defaults.
4. Require a caller-selected horizon of `15m`, `1h`, or `4h`. Use separate requests when the caller explicitly wants multiple horizons. This profile does not ask the model to choose a horizon.
5. Copy the registered question and candidates exactly, including IDs, order, instructions, and interval descriptions. Do not paraphrase, translate, rename, or manually rescale them. If the returned template cannot represent the caller's inputs, report the mismatch and obtain the supported contract instead of fabricating an adaptation.
6. Submit the resulting body to `POST /v1/systemone` on the configured service with the API key.

The snapshot's 12 state fields and `return_bin_0` through `return_bin_6` describe that artifact. Website examples with seven state fields and `bin_0` through `bin_6` must not be mixed into it. Use the fetched template to determine the actual field schema and candidate keys.

## Read the result

The output is a probability distribution over seven **gross-return** intervals. Read all probabilities by the returned template's candidate IDs. Validate completeness, finite values in [0, 1], and a sum close to 1 using an appropriate numerical tolerance. Preserve valid zeros and surface invalid distributions as errors rather than silently renormalizing them.

Show the interval descriptions, asset, and caller-selected horizon with the distribution. Fees are separate from gross return. Cost, entry timing, and execution eligibility must follow the caller's inputs and the template contract; do not infer them from the most likely bin.

The application strategy decides long/short/skip, position size, and execution. A selected bin is not itself a trading instruction. Exact expected return cannot be recovered from interval probabilities without assumptions about within-bin returns and unbounded tails.

## Validation status

The template retrieval command is documented from the owner's supplied workflow. No authenticated template retrieval or live forecast was performed while authoring this skill. Keep fixture checks distinct from service validation.
