# Local Agents

This directory contains repo-local agent role definitions for manual use.

These files do not auto-run on their own. The intended pattern is:

1. Read the relevant agent file in `.codex/agents/`
2. Spawn or brief a subagent with that role
3. Pass explicit scope: files, commit range, feature, or question
4. Reuse the same subagent for close follow-up work when context still helps

## How To Use

Use these agents when you want focused help instead of a generic assistant. Keep prompts concrete. Good prompts specify:

- what to work on
- which files or commit range matter
- whether the job is implementation, review, or test-focused
- any output expectation, such as "reply with findings only"

Example pattern:

```text
Read .codex/agents/backend-engineer.md
Spawn a subagent with those instructions
Task: implement the trade endpoint validation in backend/api/trades.py and backend/tests/test_trades.py
```

## Agents

### reviewer

**Purpose:** Review plans, diffs, and code for bugs, regressions, unsafe assumptions, and missing tests.

**When to use:**
- Before committing or pushing
- After a feature design changes
- When you want a second opinion on a patch or spec

**When not to use:**
- When you want code written from scratch
- When the task is implementation rather than critique

**Example prompts:**
- `Review the last commit and return findings only with file references.`
- `Review planning/PLAN.md for contradictions, unsafe requirements, and underspecified areas.`

### frontend-engineer

**Purpose:** Build and improve the Next.js frontend, including layout, watchlist UI, charts, chat UI, SSE consumption, and styling.

**When to use:**
- Building the watchlist, chart area, positions table, or chat panel
- Fixing rendering, interaction, or responsiveness issues
- Wiring frontend state to SSE or API responses

**When not to use:**
- When the change is mainly backend validation or persistence
- When the problem is about market-data generation rather than UI consumption

**Example prompts:**
- `Implement the watchlist panel in the Next.js frontend with live price updates from /api/stream/prices.`
- `Review the chat sidebar UI for layout problems, missing loading states, and responsive issues.`

### backend-engineer

**Purpose:** Build and improve the FastAPI backend, including routes, persistence, trade logic, schema initialization, and validation.

**When to use:**
- Implementing portfolio, trade, or watchlist endpoints
- Designing database initialization and persistence behavior
- Hardening validation and business rules

**When not to use:**
- When the task is mainly prompt design or model-output handling
- When the issue is frontend rendering or styling

**Example prompts:**
- `Implement POST /api/portfolio/trade with strict validation and transaction-safe position updates.`
- `Review the backend startup flow for DB initialization races and health-check readiness issues.`

### market-data-engineer

**Purpose:** Build and improve the simulator, live market-data adapter, price cache, SSE publishing, and streaming semantics.

**When to use:**
- Building the simulated quote engine
- Wiring a real market-data source into the same interface
- Fixing stale prices, SSE cadence, reconnection, or cache consistency

**When not to use:**
- When the task is mainly frontend visualization
- When the task is about chat prompts or trade validation logic

**Example prompts:**
- `Implement a price simulator with realistic seed prices, correlated movement, and 500ms updates.`
- `Review the SSE design for wasteful fanout, stale cache reads, and reconnection edge cases.`

### llm-engineer

**Purpose:** Build and improve the LLM chat workflow, including LiteLLM/OpenRouter integration, prompt structure, structured outputs, mock mode, and safe action parsing.

**When to use:**
- Designing or changing the chat prompt and output schema
- Adding structured-output parsing or mock responses
- Hardening the model-to-action boundary

**When not to use:**
- When the task is core trade-execution logic in the backend
- When the issue is SSE delivery or market-data generation

**Example prompts:**
- `Implement structured-output parsing for chat responses and reject malformed action payloads.`
- `Review the prompt and schema flow for prompt-injection risk and brittle assumptions.`

### qa-engineer

**Purpose:** Design and improve unit, integration, and end-to-end coverage for portfolio logic, streaming behavior, watchlist flows, and chat-driven actions.

**When to use:**
- Adding regression coverage for a new feature
- Identifying test gaps before merge
- Building deterministic LLM mock tests or E2E scenarios

**When not to use:**
- When you need architecture design or implementation ownership
- When you want a review of product requirements rather than test strategy

**Example prompts:**
- `Add backend tests for insufficient-cash buys, oversell attempts, and post-trade portfolio snapshots.`
- `Design E2E coverage for watchlist CRUD, SSE reconnect, and mocked AI-triggered trade execution.`
