# Sticky Notes — Spec-Driven Agentic Development Demo

## Project Goal

This repository demonstrates both a small Sticky Notes app and a controlled,
AI-agent-assisted software development workflow. Requirements are discovered,
locked before implementation, handed to a build agent, verified against
acceptance criteria, and delivered for human review.

## Agentic Development Workflow

```text
Requirement / Goal
        ↓
Discovery Agent
        ↓
DISCOVER → QUESTION → LOCK
        ↓
Specification → Handoff → Build Agent
        ↓
Readiness Check
   ├── NOT_READY_FOR_BUILD → Discovery / Specification
   └── READY_FOR_BUILD
        ↓
Implementation Plan → Build → Automated Tests
        ↓
Acceptance Criteria Verification → Delivery Report
        ↓
Human Review → READY_FOR_REVIEW
```

Principles:

- The locked specification is the source of truth.
- Acceptance Criteria define Done.
- A Build Agent must not guess missing requirements.
- No check is reported PASS without verification evidence.
- Human review remains the final gate.

## Workflow Artifacts

- [specs/sticky-note.md](specs/sticky-note.md): locked product requirements, API contract, and AC-1–AC-10.
- [handoff.md](handoff.md): implementation instructions and scope boundaries for the Build Agent.
- [plan.md](plan.md): implementation slices and AC verification map.
- [delivery-report.md](delivery-report.md): implementation history and acceptance evidence, separated into automated and manual verification.

## Architecture

```text
User → React → FastAPI → SQLAlchemy → PostgreSQL
```

## Tech Stack

- React with Vite
- FastAPI and Pydantic
- SQLAlchemy
- PostgreSQL 16
- Docker Compose

## Run Locally

Requires Docker Desktop with its Linux container engine and Docker Compose v2.

```powershell
Copy-Item .env.example .env
# Set a private local POSTGRES_PASSWORD in .env.
docker compose up --build
```

Open the UI at <http://localhost:5173>, API at <http://localhost:8000>, and API
docs at <http://localhost:8000/docs>. PostgreSQL data lives in the named
`postgres_data` volume. Stop with `Ctrl+C` then `docker compose down`; this
preserves the database. Do not use `docker compose down -v` unless deliberately
erasing local demo data.

## Automated Testing

Backend tests use pytest, FastAPI TestClient, and PostgreSQL (SQLite is not used
to claim PostgreSQL behavior). They require an isolated test database. For
example, start a separate PostgreSQL test container on an unused local port and
set `DATABASE_URL` and `TEST_DATABASE_URL` to its database before running:

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest -q
```

Tests create one UUID-named schema in the configured PostgreSQL test database,
run each test in that schema, then drop only that schema. Never point these
variables at the developer Compose database or production. The CI workflow uses
an ephemeral PostgreSQL service container.

Frontend verification:

```powershell
cd frontend
npm ci
npm run build
npm audit --audit-level=high
```

Automated UI E2E is not configured; browser refresh persistence remains manual
reviewer verification as recorded in the delivery report.

## Acceptance Criteria

AC-1 create; AC-2 list and UI rendering; AC-3 field edit; AC-4 hard delete;
AC-5 status transitions; AC-6 validation; AC-7 PostgreSQL persistence after app
restart; AC-8 browser refresh persistence; AC-9 API response codes; AC-10 clean
local Compose startup. See the [locked specification](specs/sticky-note.md)
for exact steps and expected outcomes.

## CI Pipeline

```text
Push / Pull Request to main
        ↓
Backend tests (ephemeral PostgreSQL)
        ↓
Frontend npm ci + production build
        ↓
npm audit (high severity threshold)
        ↓
PASS / FAIL
```

Workflow: [.github/workflows/ci.yml](.github/workflows/ci.yml). It does not
deploy, publish images, use repository secrets, or modify repository settings.
The workflow is configured locally but GitHub Actions has not been run remotely
from this workspace; see [delivery-report.md](delivery-report.md).
