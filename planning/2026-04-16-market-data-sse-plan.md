# Market Data And SSE Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a simulated market-data backend with an in-memory price cache and an SSE endpoint that streams price updates.

**Architecture:** This checkpoint adds a dedicated `market_data` subsystem under `backend/app/` and wires it into the existing FastAPI lifespan startup. The simulator generates seeded prices, the cache stores current and previous values, and the SSE route exposes live updates without introducing watchlist persistence or frontend integration yet.

**Tech Stack:** Python 3.9+, FastAPI, StreamingResponse, asyncio, pytest, httpx/TestClient, Markdown notes

---

## File Structure

- Create: `backend/app/market_data/__init__.py` — package marker for market-data subsystem
- Create: `backend/app/market_data/types.py` — typed structures for price updates and cache records
- Create: `backend/app/market_data/simulator.py` — seeded simulator and tick generation logic
- Create: `backend/app/market_data/cache.py` — in-memory latest/previous price cache
- Create: `backend/app/market_data/service.py` — market-data service lifecycle and background tick loop
- Create: `backend/app/routes/__init__.py` — routes package marker
- Create: `backend/app/routes/stream.py` — SSE route for `GET /api/stream/prices`
- Modify: `backend/app/main.py` — wire the market-data service into lifespan and include the stream route
- Create: `backend/tests/test_market_data.py` — simulator and cache behavior tests
- Create: `backend/tests/test_stream.py` — SSE endpoint tests
- Modify: `notes/01-feature-map.md` — mark live market-data streaming as implemented
- Modify: `notes/02-system-structure.md` — describe the market-data subsystem and stream route ownership
- Modify: `notes/03-data-flows.md` — document implemented backend market-data flow
- Create: `notes/checkpoints/02-market-data-and-sse.md` — checkpoint 2 implementation and verification summary

### Task 1: Failing Tests For Simulator, Cache, And SSE

**Files:**
- Create: `backend/tests/test_market_data.py`
- Create: `backend/tests/test_stream.py`

- [ ] **Step 1: Write failing simulator and cache tests**

Add tests that express these behaviors:
- the simulator seeds a default ticker set with price, previous price, and timestamp fields
- a tick updates prices while keeping required fields valid
- the cache stores previous and current values correctly for a ticker

- [ ] **Step 2: Write failing stream tests**

Add tests that express these behaviors:
- `GET /api/stream/prices` responds with `text/event-stream`
- streamed payload chunks contain `ticker`, `price`, `previous_price`, `timestamp`, and `direction`
- app startup makes seeded market data available before the first stream read

- [ ] **Step 3: Run the targeted tests to verify RED**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_market_data.py tests/test_stream.py -q
```

Expected:
- test collection succeeds
- tests fail because the market-data subsystem and stream route do not exist yet

### Task 2: Implement Simulator, Cache, And Service

**Files:**
- Create: `backend/app/market_data/__init__.py`
- Create: `backend/app/market_data/types.py`
- Create: `backend/app/market_data/simulator.py`
- Create: `backend/app/market_data/cache.py`
- Create: `backend/app/market_data/service.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Implement the typed market-data structures**

Create reusable typed structures for:
- price updates produced by the simulator
- cache records with current and previous price

- [ ] **Step 2: Implement the seeded simulator**

Add a simulator that:
- seeds a fixed default ticker set
- emits realistic initial prices
- updates prices on tick with small movements
- computes `direction` from price movement

- [ ] **Step 3: Implement the in-memory cache**

Add a cache that:
- stores latest record by ticker
- keeps previous price for each update
- exposes a snapshot read API for streaming

- [ ] **Step 4: Implement the market-data service**

Add a service that:
- constructs the simulator
- seeds the cache during startup
- starts an asyncio task to advance ticks on an interval
- stops cleanly during app shutdown

- [ ] **Step 5: Wire the service into FastAPI lifespan**

Update `backend/app/main.py` so startup:
- runs existing DB initialization
- constructs and starts the market-data service
- stores it on `app.state`

### Task 3: Implement The SSE Route

**Files:**
- Create: `backend/app/routes/__init__.py`
- Create: `backend/app/routes/stream.py`
- Modify: `backend/app/main.py`

- [ ] **Step 1: Add the SSE route**

Implement `GET /api/stream/prices` using `StreamingResponse` with `media_type="text/event-stream"`.

- [ ] **Step 2: Stream a consistent payload shape**

Emit update events that serialize to a JSON payload with:

```json
{
  "ticker": "AAPL",
  "price": 191.42,
  "previous_price": 191.10,
  "timestamp": "2026-04-16T12:34:56Z",
  "direction": "up"
}
```

- [ ] **Step 3: Re-run the targeted tests to verify GREEN**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_market_data.py tests/test_stream.py -q
```

Expected:
- all checkpoint 2 targeted tests pass

### Task 4: Notes Update, Full Verification, And Publish

**Files:**
- Modify: `notes/01-feature-map.md`
- Modify: `notes/02-system-structure.md`
- Modify: `notes/03-data-flows.md`
- Create: `notes/checkpoints/02-market-data-and-sse.md`

- [ ] **Step 1: Update the notes**

Document:
- the new market-data subsystem
- the implemented market-data runtime flow
- the SSE endpoint and current limitations

- [ ] **Step 2: Run full backend verification**

Run:

```bash
cd backend && .venv/bin/python -m pytest -q
```

and:

```bash
git status -sb
```

Expected:
- all backend tests pass
- worktree contains only intended checkpoint 2 changes plus any unrelated pre-existing files

- [ ] **Step 3: Record verification results in the checkpoint note**

Append:
- commands run
- pass/fail status
- what you can inspect manually after the checkpoint

- [ ] **Step 4: Commit checkpoint 2**

```bash
git add backend notes planning
git commit -m "Add market data simulation and SSE streaming"
```

- [ ] **Step 5: Push checkpoint 2**

```bash
git push origin main
```
