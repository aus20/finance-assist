# Foundation Checkpoint 01 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Establish the first runnable project foundation with explanatory notes, a backend skeleton, startup-safe initialization, a health endpoint, and backend tests.

**Architecture:** This checkpoint creates the backend as a small FastAPI service with an explicit startup initialization path instead of lazy first-request setup. Documentation for the project structure and data flow lives in a new `notes/` directory so progress is visible and reviewable alongside code.

**Tech Stack:** Python 3.9+, FastAPI, Uvicorn, pytest, httpx, SQLite path configuration, Markdown notes

---

## File Structure

- Create: `notes/00-project-overview.md` — concise introduction to the project and checkpoint strategy
- Create: `notes/01-feature-map.md` — feature groups and current implementation status
- Create: `notes/02-system-structure.md` — top-level directory and component responsibilities
- Create: `notes/03-data-flows.md` — high-level request/data flow descriptions for the planned system
- Create: `notes/checkpoints/01-foundation.md` — what checkpoint 1 adds and how it is verified
- Create: `backend/pyproject.toml` — backend package metadata and dependencies
- Create: `backend/app/__init__.py` — backend package marker
- Create: `backend/app/config.py` — configuration for DB path and app settings
- Create: `backend/app/bootstrap.py` — startup initialization helpers
- Create: `backend/app/main.py` — FastAPI app entrypoint, startup lifecycle, and `/api/health`
- Create: `backend/tests/conftest.py` — test client fixture and isolated repo-level DB cleanup for each test run
- Create: `backend/tests/test_health.py` — tests covering startup init and health endpoint behavior
- Create: `db/.gitkeep` — ensure DB directory exists in repo

### Task 1: Notes Foundation

**Files:**
- Create: `notes/00-project-overview.md`
- Create: `notes/01-feature-map.md`
- Create: `notes/02-system-structure.md`
- Create: `notes/03-data-flows.md`
- Create: `notes/checkpoints/01-foundation.md`

- [ ] **Step 1: Write the documentation files**

Write concise Markdown notes that explain:
- the project goal and current checkpoint strategy
- planned feature groups and which are not implemented yet
- repo structure and responsibility boundaries
- the intended system data flows: health, market data, trade flow, chat flow
- checkpoint 1 scope, non-goals, and verification commands

- [ ] **Step 2: Review notes for consistency with `planning/PLAN.md` and `planning/REVIEW.md`**

Check that the notes:
- align with the chosen checkpoint scope
- do not claim LLM, market data, or frontend features already exist
- reflect the current decision to initialize backend state during startup

- [ ] **Step 3: Commit the notes checkpoint**

```bash
git add notes db/.gitkeep
git commit -m "Add foundation notes and project structure docs"
```

### Task 2: Backend Skeleton With Startup Initialization

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/app/__init__.py`
- Create: `backend/app/config.py`
- Create: `backend/app/bootstrap.py`
- Create: `backend/app/main.py`
- Modify: `notes/checkpoints/01-foundation.md`

- [ ] **Step 1: Write the failing health test first**

Create a failing test in `backend/tests/test_health.py` that expects:
- FastAPI app responds on `GET /api/health`
- response status is `200`
- response JSON includes a healthy status and configured database path

- [ ] **Step 2: Run the backend health test to verify it fails**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_health.py -q
```

Expected:
- test collection runs
- test fails because app code does not exist yet

- [ ] **Step 3: Implement the minimal backend skeleton**

Implement:
- backend dependency definitions in `backend/pyproject.toml`
- a FastAPI app entrypoint in `backend/app/main.py`
- startup initialization in `backend/app/bootstrap.py`
- config object with DB path defaulting to `db/finally.db`
- `/api/health` route returning structured JSON such as:

```json
{
  "status": "ok",
  "database_path": "db/finally.db",
  "initialized": true
}
```

- [ ] **Step 4: Re-run the backend health test to verify it passes**

Run:

```bash
cd backend && .venv/bin/python -m pytest tests/test_health.py -q
```

Expected:
- health test passes

- [ ] **Step 5: Update checkpoint note with actual implementation details**

Document:
- created backend files
- health endpoint contract
- startup initialization approach

- [ ] **Step 6: Commit the backend skeleton checkpoint**

```bash
git add backend notes/checkpoints/01-foundation.md
git commit -m "Add backend foundation with health endpoint"
```

### Task 3: Verification And Publish

**Files:**
- Modify: `notes/checkpoints/01-foundation.md`

- [ ] **Step 1: Run the full checkpoint 1 verification commands**

Run:

```bash
cd backend && .venv/bin/python -m pytest -q
```

and:

```bash
git status -sb
```

Expected:
- backend tests pass
- worktree only contains intended changes before final push

- [ ] **Step 2: Record verification results in the checkpoint note**

Append:
- commands run
- pass/fail status
- any current limitations

- [ ] **Step 3: Push the checkpoint**

```bash
git push origin main
```
