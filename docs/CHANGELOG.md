# CHANGELOG

## 2026-03-14

### Added
- `docs/ARCHIE_ZEABUR_RUNBOOK.md`
- `docs/ARCHIE_AUTOMATION_MIGRATION_GUIDE.md`
- `docs/CHANGELOG.md`

### Infrastructure / Deployment
- Added root `Dockerfile` to force Zeabur Python API deployment (avoid Caddy static mis-detection)
- Added `.github/workflows/deploy.yml` and `scripts/deploy_remote.sh`
- Added `docker-compose.yml`, `.env.example`, and DB init SQL for stack portability

### Tooling
- Added `archie-tools/archie_push.py`
- Added `archie-tools/archie_search.py`
- Added `archie-tools/subjects_tags.md`

### Fixes (from real deployment)
- Corrected `POSTGRES_URL` requirement to full DSN (`postgresql://...`)
- Corrected internal host usage for `OLLAMA_URL`/`QDRANT_URL`
- Documented schema initialization and end-to-end verification steps
