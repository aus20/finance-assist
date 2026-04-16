# System Structure

## Repository Roles

- `frontend/`: planned static web app for the terminal UI
- `backend/`: FastAPI service, database initialization, APIs, and background work
- `db/`: runtime SQLite storage location in the repo tree
- `planning/`: source of shared project guidance and review criteria
- `notes/`: concise working documentation for checkpoint progress

## Backend Boundaries

The backend owns:
- app startup and readiness initialization
- database path selection and schema/bootstrap logic
- API endpoints and background tasks
- market-data simulation and cache runtime
- `backend/app/routes/stream.py` for the SSE price stream

The backend does not yet own:
- rendered UI
- frontend market-data rendering
- watchlist CRUD
- portfolio state management
- LLM orchestration implementation
- trade execution logic

## Initialization Model

Startup initialization is the chosen path for this checkpoint. The service prepares `db/finally.db` during process startup, seeds market data into memory, and stores the market-data service on `app.state`.

The SSE route in `backend/app/routes/stream.py` reads the seeded cache immediately when a client connects, emits the current snapshot as `data: {...}` events, and then keeps the connection open. Later simulator ticks are pushed through per-client subscriber queues so connected clients can observe new price updates on the same stream.
