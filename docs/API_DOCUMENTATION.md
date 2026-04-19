# API Documentation

Base URL: `http://localhost:8000`

## Endpoints
- `GET /health`
- `GET /health/live`
- `GET /health/ready`
- `GET /health/capabilities`
- `POST /check`
- `POST /fix`
- `POST /quality`
- `POST /check-and-fix`

## Access control
Production-facing deployments should use API key mode:

- `PRODUCTION=true`
- `API_AUTH_MODE=api_key`
- `API_KEYS=key1,key2`
- Request header: `X-API-Key` (configurable via `API_KEY_HEADER`)

If production mode is enabled with auth disabled and no explicit override, protected endpoints return `503` (`AUTH_CONFIG_ERROR`).

## Health contract
Health semantics are split:

- `/health/live`: process liveness only
- `/health/ready`: runtime readiness (auth/rate-limit backend wiring)
- `/health/capabilities`: ML capability and degraded-mode state
- `/health`: backward-compatible aggregate

`/health` includes:
- `status`: `healthy`, `degraded`, or `not_ready`
- `ml_model_loaded`
- `degraded_reason` (when degraded)
- `auth_mode`
- `rate_limit_backend`
- `max_code_size`
- `rate_limit_per_minute`

## Request limits
`/check`, `/fix`, `/quality`, and `/check-and-fix` enforce the same max payload size (`MAX_CODE_SIZE`, default `100000` chars).
Oversized payloads return `413`.

## Structured error format
Errors return:
```json
{
  "detail": {
    "error_code": "PAYLOAD_TOO_LARGE",
    "message": "code exceeds maximum allowed size (100000 characters)"
  }
}
```

## Language override
`POST /check` and `POST /check-and-fix` accept optional `language` override:
- `Python`
- `Java`
- `C`
- `C++`
- `JavaScript`

Unsupported language and unsupported fix `error_type` values are rejected with `422` validation errors.

## Rate limiting
Rate limiting is configured with:

- `RATE_LIMIT_PER_MINUTE`
- `RATE_LIMIT_BACKEND=memory|redis`
- `RATE_LIMIT_REDIS_URL` (required for redis backend)
- `RATE_LIMIT_KEY_HEADER` (identity override, defaults to `X-API-Key`)

Memory mode is default for local development; redis mode provides a shared-store seam for multi-worker/multi-instance deployments.

Exceeding limit returns `429` with `RATE_LIMIT_EXCEEDED`.

## Fix verification semantics
`POST /fix` and `POST /check-and-fix` separate generation from verification:

- `generated`: fixer produced a suggestion/candidate
- `verified`: shared-engine re-analysis confirmed improvement
- `success`: true only when verified improvement/removal was confirmed
- `verification.status`: one of
  - `verified_removed`
  - `verified_improved`
  - `unchanged`
  - `worsened`
  - `not_verified`

## CORS
Configure origins with `CORS_ORIGINS` (comma-separated).
If `*` is used, `allow_credentials` is automatically disabled.

## Docs exposure
Swagger/ReDoc exposure is configurable with `ENABLE_API_DOCS`.
Production-facing setups should default this to `false` unless running in a trusted environment.

## Example: check
```bash
curl -X POST http://localhost:8000/check \
  -H "Content-Type: application/json" \
  -d "{\"code\":\"console.log(1);\",\"language\":\"JavaScript\"}"
```
