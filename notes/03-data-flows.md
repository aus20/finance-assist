# Data Flows

These are the intended high-level flows for the system. They describe the target architecture, not completed features.

## Health Flow

1. The backend starts.
2. Startup initialization prepares the SQLite path and any required schema or seed state.
3. `GET /api/health` reports readiness only after startup work has completed.

## Market Data Flow

1. A market-data provider or simulator produces price updates.
2. The backend stores the latest values in an internal cache or service layer.
3. The frontend will later subscribe to updates through an API stream.

## Trade Flow

1. The user will later request a buy or sell action from the UI or chat assistant.
2. The backend will validate the request and apply it to portfolio state.
3. The backend will persist the trade and update derived portfolio data.

## Chat Flow

1. The user will later send a prompt to the assistant.
2. The backend will pass context to the LLM layer.
3. The assistant may return analysis and, when supported, structured actions for the backend to validate and apply.

