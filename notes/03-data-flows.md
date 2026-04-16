# Data Flows

These are the current high-level flows for the system. They describe what is implemented in this checkpoint.

## Health Flow

1. The backend starts.
2. Startup initialization prepares the SQLite path and any required schema or seed state.
3. `GET /api/health` reports readiness only after startup work has completed.

## Market Data Flow

1. The backend seeds `backend/app/market_data/` with a fixed ticker set during startup.
2. The market-data service keeps the latest prices in an in-memory cache and advances them with background ticks.
3. `GET /api/stream/prices` returns an SSE response from `backend/app/routes/stream.py`.
4. When a client connects, the route emits the current seeded snapshot immediately from the cache.
5. The route then keeps the connection open and streams later tick updates from the market-data service through subscriber queues.

## Trade Flow

1. The user will later request a buy or sell action from the UI or chat assistant.
2. The backend will validate the request and apply it to portfolio state.
3. The backend will persist the trade and update derived portfolio data.

## Chat Flow

1. The user will later send a prompt to the assistant.
2. The backend will pass context to the LLM layer.
3. The assistant may return analysis and, when supported, structured actions for the backend to validate and apply.
