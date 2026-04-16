# Checkpoint 01: Foundation

## Scope

This checkpoint establishes the project notes, the repo storage placeholder, and the first runnable backend foundation for startup-safe initialization and health reporting.

## Non-Goals

- frontend implementation
- market data integration
- LLM integration
- trading logic
- portfolio UI
- SSE stream implementation

## Backend Implementation

- Added `backend/pyproject.toml` with Python 3.9-compatible package metadata, runtime dependencies for FastAPI and Uvicorn, and a `dev` extra for pytest and httpx.
- Added `backend/app/config.py` with a small `Settings` dataclass that centralizes the database path at `db/finally.db`.
- Added `backend/app/bootstrap.py` with `initialize_database`, which creates the database directory, ensures the SQLite file exists, and returns an initialization state object.
- Added `backend/app/main.py` with a FastAPI application using `lifespan` startup initialization instead of deprecated startup events.
- Implemented `GET /api/health` to return:

```json
{
  "status": "ok",
  "database_path": "db/finally.db",
  "initialized": true
}
```

## Verification

### Commands

- `cd backend && uv sync --extra dev`
- `cd backend && .venv/bin/python -m pytest tests/test_health.py -q`
- `cd backend && .venv/bin/python -m pytest -q`
- manual payload check through `fastapi.testclient.TestClient`

### Results

- `cd backend && uv sync --extra dev` completed successfully and created `backend/.venv`.
- `cd backend && .venv/bin/python -m pytest tests/test_health.py -q` passed: `3 passed`.
- `cd backend && .venv/bin/python -m pytest -q` passed: `3 passed`.
- Manual payload check returned HTTP `200` with `status`, `database_path`, and `initialized`.
- Startup initialization prepares the repo-level `db/finally.db` during app lifespan startup before serving requests.

### Notes

- RED verification was observed before implementation and failed because `fastapi` was not installed in the local Python 3.9.6 environment yet.
- The backend skeleton intentionally excludes market-data, trading, and LLM logic at this checkpoint.
- The current test setup assumes execution from the `backend/` directory, using the virtual environment created by `uv sync`.
- The health tests clear the repo-level database file before and after each test run so startup initialization is exercised for that run instead of relying on leftover state.
- If bootstrap state is missing, `GET /api/health` now reports `status: "starting"` with `initialized: false` instead of incorrectly reporting `ok`.
