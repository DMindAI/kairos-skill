# Kairos gateway API contract

Snapshot: 2026-11-04, from `docs/jev-decisions.md` in minara-api. Gateway DTO and validation were inspected; Kairos upstream behavior was not live-tested. V4-specific limits below are documented deployment constraints, not independently verified measurements.

## Endpoint and authentication

`POST /v1/systemone`, JSON, non-streaming. Use `Authorization: Bearer <KAIROS_API_KEY>`. Both domain and API key are user-configurable. `KAIROS_BASE_URL` defaults to `https://minara.cloud` and must be the gateway origin without `/v1`. `KAIROS_API_KEY` is required and has no default; configure it on the server and do not expose it in frontend bundles. Honor a supplied base URL rather than replacing it with the default.

Set this browser-style header explicitly on all server-side requests, rather than relying on the HTTP library's default UA:

```text
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36
```

For Python clients, include it in the request's `headers` dictionary; for server-side JavaScript clients, include it in the `headers` passed to `fetch`. Keep API keys server-side. The curl example below includes the same header.

The following is a synthetic request example, not a recorded live call. Confirm that the account can use the example model before executing:

```bash
: "${KAIROS_API_KEY:?Set KAIROS_API_KEY before calling Kairos}"
KAIROS_BASE_URL="${KAIROS_BASE_URL:-https://minara.cloud}"
KAIROS_BASE_URL="${KAIROS_BASE_URL%/}"
curl --fail-with-body --max-time 30 "$KAIROS_BASE_URL/v1/systemone" \
  -H "Authorization: Bearer $KAIROS_API_KEY" \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36' \
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

Use `task_profile: general` for business-defined long/short/skip questions, factual judgments, and holding-period questions. To have the model select a holding period, add a `choice` question to `questions`; put a caller-fixed period in `state` or `instructions`.

`news_return_v4` remains the compatibility identifier for the existing return-bin task. The caller supplies the asset, news, holding period, cost, and entry rule. Supported horizons are `15m`, `1h`, and `4h`. Load the fixed [bundled template](../assets/news-return-v4.json) and follow [the template workflow](news-return-v4.md). Keep its question and seven candidates unchanged; the output is a distribution across seven gross-return intervals and the application strategy determines trading actions.

`/v1/news/templates` is not exposed to users. Do not fetch templates from the service; this skill ships the required JSON. `task_profile` and `model_version` are Kairos extensions; do not assume support through an OpenRouter channel.

## Errors

After entering relay, errors generally use `detail: {error_type, message, code?, request_id?, upstream_request_id?}`. Earlier authentication, rate-limit, or channel-selection errors may use `error.message`; clients must handle both.

- 400/422: fix input; 413: reduce payload.
- 401/403: fix credentials or access.
- 429: bounded backoff; respect a retry delay when supplied.
- 502/503/504: bounded retry only when suitable for the application. Do not assume retries are deduplicated or free.

Retain gateway and upstream request IDs for diagnostics without logging keys or image base64. Transport failures, malformed responses, and exhausted retries must remain errors rather than defaulting to a judgment.

### Cloudflare rejection versus model permissions

Two integration issues were reported by the project owner:

- **HTTP 403 with `error code: 1010`:** Cloudflare rejected the default HTTP client UA; supplying a browser-style `User-Agent` resolved that case. Check that the outgoing request actually includes the header above. An edge rejection may be plain text or HTML rather than the API's JSON error envelope. If it persists with the header, report the edge error and request identifier; do not repeatedly retry or mislabel it as invalid credentials.
- **`Dmind/Kairos` unavailable in the key's group:** a valid key can still lack model access. Ask the user to check whether the API key belongs to a Kairos-enabled group, whether that group exposes the requested model, and whether key-level model restrictions allow it. The `default` group is not guaranteed to include Kairos. Suggested message: "This API key cannot access the requested Kairos model. Check whether the key belongs to a Kairos-enabled group and whether its model permissions include this model."

Diagnose using the response body as well as the HTTP status. Do not change group assignments or substitute credentials automatically. These are user-reported integration findings, not live requests performed while writing this reference.
