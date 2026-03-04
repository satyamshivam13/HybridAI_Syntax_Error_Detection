# API Documentation

Base URL: `http://localhost:8000`

## Endpoints
- `GET /health`
- `POST /check`
- `POST /fix`
- `POST /quality`
- `POST /check-and-fix`

## Health contract
`/health` returns:
- `status`: `healthy` or `degraded`
- `ml_model_loaded`: boolean
- `degraded_reason`: present when degraded
- `max_code_size`
- `rate_limit_per_minute`

## Request limits
`/check`, `/fix`, and `/quality` enforce the same max payload size (`MAX_CODE_SIZE`, default `100000` chars).
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

## Rate limiting
Rate limiting is active per client IP using `RATE_LIMIT_PER_MINUTE` (default: `100`).
Exceeding limit returns `429` with `RATE_LIMIT_EXCEEDED`.

## CORS
Configure origins with `CORS_ORIGINS` (comma-separated).
If `*` is used, `allow_credentials` is automatically disabled.

## Example: check
```bash
curl -X POST http://localhost:8000/check \
  -H "Content-Type: application/json" \
  -d "{\"code\":\"console.log(1);\",\"language\":\"JavaScript\"}"
```
