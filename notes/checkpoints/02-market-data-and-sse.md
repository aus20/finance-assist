# Checkpoint 02: Market Data And SSE

## Scope

This checkpoint adds backend market-data simulation and an SSE price stream. The work lives in `backend/app/market_data/` and `backend/app/routes/stream.py`.

## What Exists

- `backend/app/market_data/` contains the simulator, cache, types, and service lifecycle.
- `backend/app/main.py` starts the market-data service during app lifespan startup.
- `GET /api/stream/prices` in `backend/app/routes/stream.py` returns `text/event-stream`.
- The stream emits the current snapshot immediately and keeps the connection open for later price updates.
- The initial snapshot handoff is atomic, so a newly connected client does not receive the same tick twice during subscription setup.
- `MarketDataService.start()` can be called again after `stop()` without losing the seeded cache.

## Current Limitation

The stream is still intentionally simple. It relays in-memory simulator updates to connected clients, but it does not yet support resumable subscriptions, event IDs, or external market-data sources.

## Reviewer Inspection

A reviewer can manually inspect:

- the stream endpoint at `GET /api/stream/prices`
- the seeded backend state under `app.state.market_data`
- the repo-level SQLite file at `db/finally.db` after startup initialization has run

## Verification

### Commands

- `cd backend && .venv/bin/python -m pytest tests/test_market_data.py tests/test_stream.py -q`
- `cd backend && .venv/bin/python -m pytest -q`
- manual stream inspection through `fastapi.testclient.TestClient`

### Results

- `cd backend && .venv/bin/python -m pytest tests/test_market_data.py tests/test_stream.py -q` passed: `10 passed`
- `cd backend && .venv/bin/python -m pytest -q` passed: `13 passed`
- manual stream inspection returned HTTP `200`
- manual stream inspection returned `content-type: text/event-stream; charset=utf-8`
- manual stream inspection produced initial `data: {...}` events for the default ticker set
- a same-connection manual check observed a later `AAPL` update with a changed `price` and `previous_price`

### What You Can Check Manually

- Run the backend app and call `GET /api/stream/prices` to see streamed price events.
- Keep the SSE connection open long enough to observe later updates arriving on the same response.
- Inspect `db/finally.db` after app startup to confirm the repo-level SQLite target still exists.
- Read the subsystem files in `backend/app/market_data/` to see how seed prices, cache snapshots, and ticks are modeled.

## Not In Scope

- frontend integration
- watchlist CRUD
- portfolio logic
- LLM behavior
- trade execution
