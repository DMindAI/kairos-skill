# Kairos gateway API contract

Snapshot: 2026-11-04, from `docs/jev-decisions.md` in minara-api. Gateway DTO and validation were inspected; Kairos upstream behavior was not live-tested. V4-specific limits below are documented deployment constraints, not independently verified measurements.

## Endpoint and authentication

`POST /v1/systemone`, JSON, non-streaming. Use `Authorization: Bearer <MINARA_API_KEY>`. Both domain and API key are user-configurable. `MINARA_BASE_URL` defaults to `https://minara.cloud` and must be the gateway origin without `/v1`. `MINARA_API_KEY` is required and has no default; configure it on the server and do not expose it in frontend bundles. Honor a supplied base URL rather than replacing it with the default.

The following is a synthetic request example, not a recorded live call. Confirm that the account can use the example model before executing:

```bash
: "${MINARA_API_KEY:?Set MINARA_API_KEY before calling Kairos}"
MINARA_BASE_URL="${MINARA_BASE_URL:-https://minara.cloud}"
MINARA_BASE_URL="${MINARA_BASE_URL%/}"
curl --fail-with-body --max-time 30 "$MINARA_BASE_URL/v1/systemone" \
  -H "Authorization: Bearer $MINARA_API_KEY" \
  -H 'Content-Type: application/json' \
  --data-binary '{
    "model": "Dmind/Kairos",
    "state": {"message": "I was charged twice. Please refund the duplicate."},
    "questions": {
      "refund_requested": {
        "type": "noul",
        "instructions": "Does the customer explicitly request a refund in message?"
      },
      "topic": {
        "type": "choice",
        "instructions": "Which topic best describes message?",
        "criteria": {
          "billing": "Charges, invoices, or refunds",
          "access": "Login or account access",
          "other": "A topic outside billing and account access"
        }
      }
    }
  }'
```

## Request types and limits

Required fields: `model`, `state`, `questions` (map from question ID to question). `state` and question `instructions` accept a string, object, or array.

| Type | Criteria | Answer fields |
| --- | --- | --- |
| `noul` | Optional object containing `true` and `false` descriptions, neither null | `type`, `noul` (0–1) |
| `choice` | Named options with descriptions | `type`, `choice`, `probabilities`, `confidence` |
| `score` | Ordered list of 2–10 descriptions, none null | `type`, `score`, `legend`, `probabilities`, `confidence` |

Choice descriptions accept string/object/array/null; score and noul descriptions accept string/object/array. Prefer descriptive, non-null criteria for understandable examples.

Use the stricter applicable limit:

| Constraint | Gateway | Documented Kairos V4 |
| --- | --- | --- |
| Questions per request | 1–1024 | 1–8 |
| Choice options | 2–255 | 2–26 |
| JSON body including base64 | 1 MiB | Gateway limit still applies |
| Context per question | Deployment-dependent | 4096 tokens including images |

Omit `stream`; `true` is rejected. Do not import Jev `Box` support into Kairos examples: the public gateway accepts only `noul`, `choice`, and `score`.

## Response interpretation and usage

Responses contain `model`, `answers` keyed by question ID, and `usage`. Noul is a probability. Score is a probability-weighted level index and may be fractional; its legend explains the indices. Preserve zero probabilities, scores, confidence, and token counts.

Usage includes `input_tokens`, `output_tokens`, and optionally `evaluated_questions`. Kairos candidate scoring reports zero output tokens. Input tokens sum the question inputs, including visual tokens; do not assume shared state is billed only once or multiply the returned usage by question count again. Actual charges depend on configured prices and groups and should be checked in usage logs.

Optional metadata may include `model_version`, `prompt_version`, `calibration_version`, `task_profile`, `request_id`, and `timings_ms`. The response model identifier may differ from the requested catalog name.

## Images

Only use a model/channel that supports images. Put each image in:

```json
{"assets":{"photo-id":{"type":"image","format":"png","data_base64":"<standard padded base64 of PNG bytes>"}}}
```

Reference its asset ID in a string value inside `state`, `instructions`, or `criteria`, for example `state: {"photo": "photo-id"}`. Every image must be referenced; keys and question IDs are not references. The placeholder above is not executable image data.

- Gateway: up to 4 images; whole JSON body at most 1 MiB including base64; dimensions at most 4096 pixels per edge.
- Kairos V4: each edge must be 280–1568 pixels. Resize before encoding.
- Accept PNG/JPG/JPEG with matching content. Use plain standard padded base64, without a data URL prefix or whitespace.
- Remote image URLs, multipart, audio, and video are unsupported here. Decision Playground separately limits original files to 512 KiB combined.
- The gateway adds the required upstream image header for direct Kairos. Clients do not need to add it. OpenRouter channels do not accept these image assets.

## Task profiles

The project owner confirmed that the bundled news JSON is authoritative and the public News profile page is awaiting correction; see [the documented differences](news-trading.md). Use this artifact, not the website's conflicting seven-field schema or bin IDs. The website's advertised Cloud template route has not been verified; no retrieval is needed to use the bundled template.

Omitting `task_profile` uses the upstream default `general`; explicit `general` supports custom questions. `task_profile` and `model_version` require a direct Kairos channel, not OpenRouter.

For `news_return_v4`, use the [fixed news workflow](news-return-v4.md) and [bundled deployment template](../assets/news-return-v4.json) supplied by the project owner. The caller chooses `15m`, `1h`, or `4h`; preserve the fixed seven-bin question and its matching cost convention. It does not automatically produce trading actions or infer that holding period. `GET /v1/news/templates` is an upstream authenticated endpoint, not a public gateway route; the bundled template avoids requiring users to retrieve it. Obtain a new verified deployment template for changes to its cost or other fixed semantics. Do not substitute arbitrary general choice questions.

## Errors

After entering relay, errors generally use `detail: {error_type, message, code?, request_id?, upstream_request_id?}`. Earlier authentication, rate-limit, or channel-selection errors may use `error.message`; clients must handle both.

- 400/422: fix input; 413: reduce payload.
- 401/403: fix credentials or access.
- 429: bounded backoff; respect a retry delay when supplied.
- 502/503/504: bounded retry only when suitable for the application. Do not assume retries are deduplicated or free.

Retain gateway and upstream request IDs for diagnostics without logging keys or image base64. Transport failures, malformed responses, and exhausted retries must remain errors rather than defaulting to a judgment.
