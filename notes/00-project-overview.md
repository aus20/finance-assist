# Project Overview

FinAlly is a planned AI-powered trading workstation with a single backend service, a future static frontend, and a SQLite-backed data store. This checkpoint establishes the first project notes plus a runnable backend foundation so the implementation path is easy to review.

Current direction:
- backend initialization happens at startup, not on the first request
- the database lives at `db/finally.db`
- the repository keeps a top-level `db/` directory so the runtime storage path is explicit

What is not done yet:
- the frontend UI
- market data delivery
- LLM chat integration
- trading actions and portfolio management

The notes in this directory are the shared reference for the checkpoint plan, review process, and the features that are actually present so far.
