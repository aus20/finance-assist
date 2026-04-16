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

The backend does not yet own:
- rendered UI
- market data ingestion implementation
- LLM orchestration implementation
- trade execution logic

## Initialization Model

Startup initialization is the chosen path for this checkpoint. The service should prepare its database state during process startup so readiness is deterministic and the health endpoint can reflect actual availability.

