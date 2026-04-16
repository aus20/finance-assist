# Market Data And SSE Design

## Goal

Add the first live runtime behavior to the backend by introducing a simulated market-data pipeline and an SSE endpoint that streams price updates. This checkpoint should stay backend-only and avoid watchlist CRUD, portfolio math, or frontend integration.

## Scope

This design covers:

- a deterministic market-data simulator with seeded default tickers
- an in-memory price cache containing current and previous values
- a background market-data service started during FastAPI lifespan startup
- `GET /api/stream/prices` as an SSE endpoint
- backend tests for simulator behavior, cache updates, and stream payload shape
- updates to the project notes to document the new runtime flow

This design does not cover:

- watchlist persistence or CRUD
- manual trading endpoints
- portfolio calculations
- frontend EventSource wiring
- LLM integration
- real market-data provider integration

## Design Choice

Recommended approach: build the simulator, cache, and SSE path together in one checkpoint.

Alternative 1: simulator and cache only.
- Lower complexity.
- Leaves the product without an externally visible live behavior.

Alternative 2: simulator, cache, SSE, and watchlist CRUD.
- More end-user value in one step.
- Blends two concerns: streaming infrastructure and persistence/API design.
- Increases checkpoint size and review surface unnecessarily.

Recommended choice:
- simulator + cache + SSE

Reasoning:
- It produces the first meaningful live system behavior.
- It keeps the checkpoint small enough to review and verify.
- It preserves a clean next checkpoint for watchlist-backed filtering and persistence.

## Architecture

Checkpoint 2 introduces a dedicated market-data subsystem inside `backend/app/market_data/`.

Proposed units:

- `backend/app/market_data/types.py`
  - shared dataclasses or typed shapes for price updates
- `backend/app/market_data/simulator.py`
  - seeded ticker defaults and tick-generation logic
- `backend/app/market_data/cache.py`
  - in-memory storage for latest and previous price state
- `backend/app/market_data/service.py`
  - background loop that advances the simulator and writes to the cache
- `backend/app/routes/stream.py`
  - SSE route definitions

Existing integration points:

- `backend/app/main.py`
  - starts and stops the market-data service in the lifespan hook
  - registers the stream route
- `notes/`
  - updated to reflect that live backend streaming now exists

This structure keeps generation, state storage, and transport separate. That separation matters because checkpoint 3 can later change which symbols are streamed without rewriting simulator or cache logic.

## Runtime Flow

On startup:

1. FastAPI lifespan begins.
2. Health/bootstrap initialization runs as it does today.
3. The market-data service constructs a simulator with default tickers.
4. The service seeds the cache with initial prices.
5. A background loop starts ticking at a fixed interval.

At each tick:

1. The simulator calculates new prices from prior values.
2. The cache updates `price`, `previous_price`, and timestamp per ticker.
3. Connected stream consumers can read the latest state from the cache.

For SSE:

1. Client connects to `GET /api/stream/prices`.
2. Backend returns `text/event-stream`.
3. Stream emits serialized price update messages on a steady cadence.
4. Each message contains at least:
   - `ticker`
   - `price`
   - `previous_price`
   - `timestamp`
   - derived change direction

## Simulator Behavior

The simulator should be intentionally simple for this checkpoint.

Requirements:

- seed realistic starting prices for a default ticker set
- produce small random movement on each tick
- preserve numeric validity across ticks
- keep interfaces deterministic enough for testing

Non-requirements for this checkpoint:

- precise financial modeling
- correlated sector movement
- event spikes
- configurable tick universes from persistence

Those can be layered in later once the delivery pipeline exists.

## Cache Contract

The cache is the single in-memory source of truth for current simulated prices.

Minimum responsibilities:

- store latest price by ticker
- retain previous price for change calculations
- expose snapshot reads for stream output
- support seeded initial state before first client request

This cache remains process-local for now. Multi-process or distributed behavior is explicitly out of scope for this checkpoint.

## SSE Contract

The SSE endpoint should prefer clarity over optimization.

Initial behavior:

- single endpoint: `GET /api/stream/prices`
- emits events for the default ticker set
- no user-specific filtering yet
- no watchlist scoping yet

Initial payload contract:

```json
{
  "ticker": "AAPL",
  "price": 191.42,
  "previous_price": 191.10,
  "timestamp": "2026-04-16T12:34:56Z",
  "direction": "up"
}
```

The endpoint can emit one event per ticker update or a compact sequence of update events, but the tests should lock down one consistent shape.

## Error Handling

Checkpoint 2 should handle errors conservatively.

- If simulator startup fails, app startup should fail rather than quietly serving a broken stream.
- If the stream loop encounters a transient runtime issue, it should not corrupt cache state.
- If no bootstrap state exists yet, health should continue to behave as defined in checkpoint 1.

Detailed retry and resilience policies are out of scope for this checkpoint.

## Testing Strategy

Backend tests should cover:

- simulator seeds default ticker prices in a valid shape
- one tick updates prices while preserving required fields
- cache preserves previous and current values correctly
- SSE endpoint responds with event-stream output
- stream payload contains the expected fields and value types
- lifespan startup makes the stream endpoint usable without manual setup

The tests should stay backend-only. No browser automation belongs in this checkpoint.

## Notes Updates

Checkpoint 2 should update:

- `notes/01-feature-map.md`
  - mark live market-data streaming as present in this checkpoint
- `notes/02-system-structure.md`
  - document the new `market_data` subsystem and route ownership
- `notes/03-data-flows.md`
  - update the market-data flow from planned to implemented backend behavior
- `notes/checkpoints/02-market-data-and-sse.md`
  - scope, implementation summary, verification commands, and limits

## Success Criteria

Checkpoint 2 is complete when:

- backend starts with simulated prices seeded in memory
- `GET /api/stream/prices` produces valid SSE output
- backend tests for simulator, cache, and stream behavior pass
- notes reflect the new runtime behavior accurately
- checkpoint is reviewed, committed, and pushed

## Risks

- SSE tests can become brittle if they assert on timing too aggressively
- a poor cache boundary will make watchlist scoping awkward in the next checkpoint
- over-designing the simulator now would slow the checkpoint without adding product value

The design avoids those risks by keeping interfaces small, process-local, and backend-only.
