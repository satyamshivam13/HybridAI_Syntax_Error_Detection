# External Integrations

**Analysis Date:** 2026-03-27

## APIs & External Services

**External APIs:**
- None required for core runtime behavior
  - Integration method: local-only analysis inside the Python process
  - Auth: none
  - Rate limits: internal request limiting only, configured in `api.py`

## Data Storage

**Databases:**
- None currently
  - Detection and reporting are file-backed rather than database-backed

**File Storage:**
- Local filesystem - models, datasets, generated results, and docs
  - Model artifacts: `models/*.pkl`
  - Datasets: `dataset/active/`, `dataset/archive/`, `dataset/merged/`
  - Evaluation outputs: `artifacts/` and `results/`

**Caching:**
- None explicitly implemented
  - Runtime state is mostly stateless per request except for in-memory API rate-limit tracking

## Authentication & Identity

**Auth Provider:**
- None
  - The API is currently open and relies on payload/rate controls rather than user identity

## Monitoring & Observability

**Error Tracking:**
- None external
  - Errors are surfaced through API responses, tests, and console logs

**Analytics:**
- None

**Logs:**
- Python logging to stdout/stderr
  - Configured in `api.py`

## CI/CD & Deployment

**Hosting:**
- Local Python runtime by default
  - API served with `uvicorn`
  - Streamlit served with `streamlit run app.py`

**CI Pipeline:**
- GitHub Actions
  - Workflow: `.github/workflows/ci.yml`
  - Runs tests and markdown link validation on push and pull request

## Environment Configuration

**Development:**
- Required env vars are documented in `.env.template`
- Secrets location: local `.env` if needed
- Mock/stub services: not needed because the product is largely self-contained

**Staging:**
- No separate staging profile documented in the repo

**Production:**
- Controlled by environment variables read by `start_api.py` and `api.py`
- ML health depends on local model artifact compatibility

## Webhooks & Callbacks

**Incoming:**
- None

**Outgoing:**
- None

## Integration Risks

- `scikit-learn==1.1.3` is effectively an integration contract with `models/*.pkl`
- Missing or incompatible model files force degraded mode in `src/ml_engine.py`
- Evaluation scripts depend on local datasets and artifacts being present in expected directories

---
*Integration audit: 2026-03-27*
*Update when adding/removing external services*
