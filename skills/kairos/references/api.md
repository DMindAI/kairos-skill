# Kairos gateway API contract

Snapshot: 2026-11-04, from `docs/jev-decisions.md` in minara-api. Gateway DTO and validation were inspected; Kairos upstream behavior was not live-tested. The owner supplied an updated upstream contract dated 2026-11-05. Its Cloud rollout is pending confirmation; upstream capacity does not override stricter gateway limits.

## Endpoint and authentication

`POST /v1/systemone`, JSON, non-streaming. Use `Authorization: Bearer <KAIROS_API_KEY>`. Both domain and API key are user-configurable. `KAIROS_BASE_URL` defaults to `https://minara.cloud` and must be the gateway origin without `/v1`. `KAIROS_API_KEY` is required and has no default; configure it on the server and do not expose it in frontend bundles. Honor a supplied base URL rather than replacing it with the default.

Use `model: DMIND/Kairos` for all requests, preserving this capitalization. Do not query a model list as a setup prerequisite. Access still depends on the API key group and model permissions.

The following is a synthetic request example, not a recorded live call. Confirm that the account can use the example model before executing:

```bash
: "${KAIROS_API_KEY:?Set KAIROS_API_KEY before calling Kairos}"
KAIROS_BASE_URL="${KAIROS_BASE_URL:-https://minara.cloud}"
KAIROS_BASE_URL="${KAIROS_BASE_URL%/}"
curl --fail-with-body --max-time 30 "$KAIROS_BASE_URL/v1/systemone" \
  -H "Authorization: Bearer $KAIROS_API_KEY" \
  -H 'Content-Type: application/json' \
  --data-binary '{
    "model": "DMIND/Kairos",
    "state": {"message": "I cannot sign in. Please help me recover access."},
    "questions": {
      "access_requested": {
        "type": "noul",
        "instructions": "Does the user explicitly request account access assistance in message?"
      },
      "topic": {
        "type": "choice",
        "instructions": "Which topic best describes message?",
        "criteria": {
          "technical": "Application errors or technical troubleshooting",
          "access": "Login or account access",
          "other": "A topic outside technical support and account access"
        }
      }
    }
  }'
```

## Request types and limits

For this Cloud integration, send `model`, `state`, and `questions` (a map from question ID to question). `state` and question `instructions` accept a nonempty string, object, or array. Question IDs must contain 1–128 characters; choice IDs must be nonempty, at most 128 characters, and contain no control characters. Use unique JSON keys and finite numbers. Do not add undocumented top-level fields. Each question independently evaluates the supplied state; later questions do not read earlier answers.

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

Usage includes `input_tokens`, `output_tokens`, and optionally `evaluated_questions`. Kairos candidate scoring reports zero output tokens. Input tokens sum the question inputs, including visual tokens. Shared state and images are counted separately for each question; do not multiply returned usage by question count again.

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
- Request-building code must automatically add `TypeSafe-Danger-Zone-Images: true` whenever the payload contains image assets. This is part of request construction, not a user configuration step. OpenRouter channels do not accept these image assets.

## Task profiles

Use `task_profile: general` for business-defined long/short/skip questions, factual judgments, and holding-period questions. To have the model select a holding period, add a `choice` question to `questions`; put a caller-fixed period in `state` or `instructions`.

`news_return` identifies the seven-bin gross-return task. The caller supplies the required state fields. Supported horizons are `15m`, `1h`, and `4h`. Load the fixed [bundled template](../assets/news-return.json) and follow [the template workflow](news-return.md). Preserve its question and seven candidate IDs; derive numeric interval descriptions from the state using the documented cross-field rule. The output is a seven-interval probability distribution.

`/v1/news/templates` is not exposed to users. Do not fetch templates from the service; this skill ships the required JSON. `task_profile` and `model_version` are Kairos extensions; do not assume support through an OpenRouter channel.

## Errors

After entering relay, errors generally use `detail: {error_type, message, code?, request_id?, upstream_request_id?}`. Earlier authentication, rate-limit, or channel-selection errors may use `error.message`; clients must handle both. The updated upstream contract uses `error: {code, message, request_id}`; preserve its code and request ID when present.

- 400/422: fix input; 413: reduce payload.
- 401/403: fix credentials or access.
- 429: bounded backoff; respect a retry delay when supplied.
- 502/503/504: bounded retry only when suitable for the application. Retries may execute another inference; request IDs do not provide deduplication.

Retain gateway and upstream request IDs for diagnostics without logging keys or image base64. Transport failures, malformed responses, and exhausted retries must remain errors rather than defaulting to a judgment.

### Model group permissions

A valid API key can still lack access to Kairos. Check whether the key belongs to a Kairos-enabled group, whether the group exposes the requested model ID, and whether key-level model restrictions allow it. The `default` group is not guaranteed to include Kairos.

Suggested message: "This API key cannot access the requested Kairos model. Check whether the key belongs to a Kairos-enabled group and whether its model permissions include the exact model ID."

Diagnose using the response body as well as the HTTP status. Do not change group assignments or substitute credentials automatically. Group-access failures were reported by the project owner; this does not imply every account has the same group configuration.

## Updated upstream contract and Cloud compatibility

The 2026-11-05 upstream documentation describes multipart image input, up to 8 images, 16 MiB per file, 4 MiB text requests, and 32 MiB image requests. It specifies 65535 context tokens per question, at most 8 image references and 2401 visual tokens per question, with repeated references counted again. These are upstream limits; do not assume this Cloud gateway exposes them until its rollout and validation are confirmed. Keep the stricter gateway constraints above for this integration.

The upstream waiting budget is documented as 600 seconds, with a suggested client connect/read timeout of 10/630 seconds. Configure timeouts for the application's latency requirements and confirmed Cloud timeout; the short curl example above may stop before upstream computation completes.

`confidence` measures distribution concentration, not calibrated correctness. For `choice`, use `probabilities` for candidate probabilities; equal maxima select the first input candidate. For `score`, indices start at zero and the result is their probability-weighted mean. `noul` has no additional probabilities or confidence field. Upstream `timings_ms` excludes the complete client-to-gateway network duration.

Automatically construct image headers, for example:

```python
headers = {"Authorization": "Bearer " + os.environ["KAIROS_API_KEY"]}
if payload.get("assets"):
    headers["TypeSafe-Danger-Zone-Images"] = "true"
```
