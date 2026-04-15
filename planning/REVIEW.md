# Review of `planning/PLAN.md`

Overall, the plan is strong on product vision and gives the implementation team a clear target. The main gaps are a few internal inconsistencies and some under-specified operational and safety contracts that should be tightened before implementation starts.

## Findings

1. **High: The database persistence story is inconsistent across sections.**
   - `planning/PLAN.md:67`, `planning/PLAN.md:101-114`, and `planning/PLAN.md:396-402` describe the SQLite file as both a project `db/` volume mount and a named Docker volume mounted at `/app/db`.
   - This is not just wording drift; it affects how the app should be started, where data persists, and what the scripts need to manage.
   - Pick one model and state it everywhere. For example, either:
     - use a bind mount from the host `db/` directory, or
     - use a named volume only and remove the claim that the repo `db/` directory is the runtime mount target.

2. **Medium: Lazy database initialization on first request is race-prone.**
   - `planning/PLAN.md:113-114` and `planning/PLAN.md:188-192` say the backend initializes schema and seed data on first request if the DB is missing or empty.
   - That is vulnerable to concurrent startup races and makes health checks less deterministic. Two requests arriving during boot can both try to create tables or seed data.
   - Prefer a startup-time initialization step guarded by an idempotent migration or a lock, and make the health endpoint reflect readiness only after initialization completes.

3. **Medium: The SSE plan is likely to become inefficient as the number of tickers or clients grows.**
   - `planning/PLAN.md:169-180` says the backend pushes updates for all known tickers every ~500ms to every connected client, even though the UI only needs a subset of those prices at any given time.
   - That is acceptable for a toy demo, but the plan currently frames the architecture as future multi-user ready. In that form, the broadcast model will waste CPU and bandwidth and make scaling harder.
   - Define whether the stream is watchlist-scoped, client-scoped, or global. If it stays global, add backpressure/delta semantics; if not, stream only subscribed symbols.

4. **High: LLM auto-execution needs stricter server-side guardrails.**
   - `planning/PLAN.md:297-328` allows the model to auto-execute trades and watchlist changes with no confirmation dialog.
   - Even in a simulated environment, the backend must treat model output as untrusted input. The plan should explicitly require schema validation, ticker normalization, quantity bounds, duplicate-action deduping, and transactional application of any side effects.
   - Also clarify how malformed or adversarial prompts are handled. The current text says validation errors are returned to the chat, but it does not say the backend rejects unsafe actions before they reach persistence or execution.

## Suggestions

- Clarify the API contract for watchlist tickers and trade requests, including allowed ticker format, quantity precision, and error responses.
- Add an explicit note that chat content and action payloads are stored and rendered as data only, never as raw HTML.
- Replace ambiguous terms like “Massive API” with the exact provider name used in implementation docs, or note the alias once and use one term consistently after that.
- Add readiness and failure-state behavior for startup, market-data polling, and LLM outage handling so the implementation has a clear fallback path.
