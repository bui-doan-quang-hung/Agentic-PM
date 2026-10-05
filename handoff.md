# Sticky Notes App — Build Agent Handoff

## Readiness

**READY_FOR_BUILD**  
The earlier blockers have been resolved by the product owner and incorporated in [specs/sticky-note.md](specs/sticky-note.md). No application implementation code has been written yet.

## Objective

Build a small local Sticky Notes web app for creating, listing, editing, deleting, and changing note status. PostgreSQL is the source of truth. The React UI must fetch persisted notes from the backend, including after browser refresh.

## Required Stack

- React frontend
- FastAPI backend
- SQLAlchemy ORM
- PostgreSQL database
- Docker Compose for local execution

Do not change this stack. Versions, dependency management, and migration/schema initialization details are build choices as long as the spec contract and clean local startup are satisfied.

## Source of Truth

The complete locked contract is [specs/sticky-note.md](specs/sticky-note.md). Read and implement its Functional Requirements, Data Model, API Contract, Business Rules, Acceptance Criteria, Run/Verify requirements, and Definition of Done. Do not rediscover, weaken, or expand the requirements.

## Locked Model and Rules

- `id`: auto-generated integer primary key.
- `title`: required string, trimmed, non-empty after trimming, max 255 characters.
- `content`: optional text.
- `priority`: `LOW`, `MEDIUM`, or `HIGH`.
- `status`: `TODO`, `DOING`, or `DONE`; defaults to `TODO` on create.
- `created_at`: set on insert and immutable.
- `updated_at`: set on insert and updated on field edits or status changes.
- Every transition among valid statuses is allowed, including direct `TODO` ↔ `DONE`.
- Delete permanently removes the PostgreSQL record.
- Do not use localStorage as the primary note store.

## Locked API

- `POST /api/notes` → `201`
- `GET /api/notes` → `200`
- `GET /api/notes/{id}` → `200`, missing ID → `404`
- `PUT /api/notes/{id}` (title/content/priority; does not change status) → `200`, missing ID → `404`
- `PATCH /api/notes/{id}/status` → `200`, invalid status → `422`, missing ID → `404`
- `DELETE /api/notes/{id}` → hard delete, `204`, missing ID → `404`
- Invalid/missing required title and invalid priority/status → `422`; rejected requests must not mutate persisted rows.

Follow the request/response field contract and timestamp semantics in the spec. Framework-default validation detail shape is acceptable.

## Required Verification

Run and record each AC-1 through AC-10 in the spec. Evidence must include API response codes and payloads, validation rejection without mutation, PostgreSQL persistence after restarting app services while retaining the database volume, and UI persistence after browser refresh. Do not report PASS without observed evidence. Also document the exact commands used.

## Scope Limits

Do not add authentication, multiple users, AI, notifications, file upload, drag and drop, search/filter, cloud deployment, or other features absent from the spec.

## Build Sequence

1. Inspect workspace and existing project files; preserve compatible work.
2. Add Docker Compose and clean-run configuration for React, FastAPI, and PostgreSQL.
3. Implement SQLAlchemy model/schema initialization and API with the locked validation and persistence rules.
4. Implement the React UI for create, list, edit, status change, and delete; load state from the backend on startup/refresh.
5. Run the services, verify each API and UI acceptance criterion, and fix any failures.
6. Create `delivery-report.md` with features, changed files, commands, AC outcomes and evidence, limitations, deviations, and final status (`READY_FOR_REVIEW` or `BLOCKED`).

No additional clarification is required to begin implementation.
