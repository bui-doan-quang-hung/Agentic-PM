# Sticky Notes App — Specification

**Status:** LOCKED  
**Phase:** SPEC complete; ready for build  
**Implementation:** Not started

## Goal

Build a small local web app for managing sticky notes. Users can create, view, edit, delete, and change the status of notes. All note data is stored in PostgreSQL and loaded from the backend, including after a browser refresh. The project demonstrates a Spec-Driven / Agentic Development workflow and prioritizes simple operation and verification.

## Functional Requirements

- **FR-1 Create:** Create a note with title, optional content, and priority. New notes start with status `TODO`.
- **FR-2 Read:** Show all notes and their fields, including status and priority. A user can retrieve a note by ID through the API.
- **FR-3 Update:** Edit title, content, and priority for an existing note. Updating these fields does not change status.
- **FR-4 Delete:** Delete an existing note permanently from PostgreSQL.
- **FR-5 Status:** Change an existing note's status to any valid status (`TODO`, `DOING`, or `DONE`). All transitions between these states are permitted.
- **FR-6 Persistence:** PostgreSQL is the source of truth. The frontend fetches notes from the backend; browser refresh and app restart must not lose stored notes, provided the PostgreSQL volume is retained.

## Non-functional Requirements

- Keep implementation and local operation suitable for a small demo project.
- Use React, FastAPI, SQLAlchemy, PostgreSQL, and Docker Compose.
- Provide repeatable local startup and documented verification steps.
- Do not use `localStorage` as the primary or authoritative note store.

## Data Model

### StickyNote

| Field | Type | Rules |
|---|---|---|
| `id` | Integer | Auto-generated primary key. |
| `title` | String, maximum 255 characters | Required; must not be empty; maximum length 255. |
| `content` | Text, nullable | Optional. |
| `priority` | Enum/string | Exactly one of `LOW`, `MEDIUM`, `HIGH`. |
| `status` | Enum/string | Exactly one of `TODO`, `DOING`, `DONE`; default `TODO` on creation. |
| `created_at` | Timestamp | Set automatically on insert; immutable afterward. |
| `updated_at` | Timestamp | Set automatically on insert and updated on note-field edits or status changes. |

PostgreSQL is mandatory. Hard deletion removes the row from the database.

## API Contract

All endpoints are under `/api/notes`. JSON request and response bodies are used where applicable. A note response contains `id`, `title`, `content`, `priority`, `status`, `created_at`, and `updated_at`.

| Method / path | Request | Success | Errors |
|---|---|---|---|
| `POST /api/notes` | JSON with required `title`, optional `content`, required `priority`; status omitted or `TODO` on create | `201`, created note JSON | `422` for invalid/missing title or invalid priority/status |
| `GET /api/notes` | None | `200`, JSON array of notes | — |
| `GET /api/notes/{id}` | Integer ID | `200`, note JSON | `404` if no note has that ID |
| `PUT /api/notes/{id}` | JSON with `title`, `content`, `priority`; status is not updated by this endpoint | `200`, updated note JSON | `404` if absent; `422` for invalid input |
| `PATCH /api/notes/{id}/status` | JSON `{ "status": "TODO" | "DOING" | "DONE" }` | `200`, updated note JSON | `404` if absent; `422` for invalid status |
| `DELETE /api/notes/{id}` | Integer ID | `204`, no response body; row is hard-deleted | `404` if absent |

FastAPI/Pydantic validation responses use HTTP `422`; exact error response text/shape may follow framework defaults. Invalid requests must not mutate stored data. The `PUT` request supplies the editable fields; a missing optional content value is treated as `null`/empty content.

## Business Rules

- Title is required, non-empty, and at most 255 characters. A title consisting only of whitespace is invalid. The implementation trims title whitespace before storage; the resulting title must remain non-empty.
- Content is optional and may be empty or null.
- Priority accepts only `LOW`, `MEDIUM`, or `HIGH`.
- Status accepts only `TODO`, `DOING`, or `DONE`.
- Any status can transition directly to either other status or remain unchanged; no sequential workflow restriction applies.
- Creating a note defaults status to `TODO` when the client omits status.
- Editing title/content/priority does not change status.
- `created_at` does not change after creation. `updated_at` changes on a successful field update or status change; it does not change on reads or rejected requests.
- Delete is a hard delete from PostgreSQL.
- PostgreSQL is authoritative. No primary note data is stored in browser localStorage.

## Acceptance Criteria

Each criterion is independently verifiable through UI/API/database evidence.

- **AC-1 Create:** `POST /api/notes` with title `Demo` and priority `MEDIUM` returns `201` with an integer ID, title `Demo`, priority `MEDIUM`, status `TODO`, and non-null timestamps. `GET /api/notes/{id}` returns the created note.
- **AC-2 Read/list:** After creating two notes with distinct titles, `GET /api/notes` returns both records with their title, content, priority, status, and timestamps. The React UI displays both notes and their statuses.
- **AC-3 Edit:** `PUT /api/notes/{id}` with changed title/content/priority returns `200`; a subsequent GET shows all supplied values, preserves status and `created_at`, and has an `updated_at` not earlier than its prior value.
- **AC-4 Delete:** `DELETE /api/notes/{id}` returns `204`; a subsequent GET by ID returns `404`, and the row is absent from `GET /api/notes` and PostgreSQL.
- **AC-5 Status:** For a note, requests setting status to each of `TODO`, `DOING`, and `DONE` each return `200` and the requested value on subsequent GET. At least one direct transition from `TODO` to `DONE` is accepted. A successful status change preserves `created_at` and updates `updated_at`.
- **AC-6 Validation:** A missing title, empty title, whitespace-only title, title longer than 255 characters, invalid priority, and invalid status each return `422`; no invalid request creates or changes a database row. A valid title of exactly 255 characters is accepted.
- **AC-7 PostgreSQL persistence:** Create a note via API, restart app services while retaining the PostgreSQL volume, then query `GET /api/notes/{id}`; it still returns `200` and the same stored fields.
- **AC-8 Refresh persistence:** Create a note, load it in the React UI, refresh the browser, and verify that the note remains visible with its stored values as loaded from the backend. The application does not rely on browser localStorage for note persistence.
- **AC-9 API codes:** Verify the documented success codes (`201`, `200`, `204`) and `404` behavior for missing IDs on get, update, status update, and delete. Invalid field values/status return `422`.
- **AC-10 Local run:** From the documented clean-checkout steps, Docker Compose starts React, FastAPI, and PostgreSQL; the UI and API become reachable, and the verification steps above can be performed.

## Tech Stack

- Frontend: React
- Backend: FastAPI
- ORM: SQLAlchemy
- Database: PostgreSQL (required source of truth)
- Containers/local orchestration: Docker Compose

Versions and dependency/migration tools are implementation choices that must preserve this contract. The database schema must be initialized repeatably for a clean local run.

## Out of Scope

- Authentication
- Multiple users
- AI functionality
- Notifications
- File uploads
- Drag and drop
- Search and filtering
- Cloud deployment
- Any other feature not explicitly listed in this specification

## Run / Verify Requirements

- Provide Docker Compose local startup instructions and required configuration values.
- Start frontend, backend, and PostgreSQL from the documented command(s).
- Initialize schema repeatably on a clean database using the chosen implementation approach.
- Provide automated tests and/or a concrete verification checklist covering every AC, including API status codes, validation, PostgreSQL persistence after app restart, and browser refresh persistence.
- For persistence verification, restart app services without removing the named PostgreSQL volume.

## Definition of Done

- All functional requirements are implemented with the specified stack.
- Note data is persisted in PostgreSQL and fetched by the UI from the backend.
- All acceptance criteria AC-1 through AC-10 have been run and their outcomes recorded.
- Docker Compose startup and verification instructions work from a clean checkout.
- No out-of-scope feature is added.
- Delivery report records changed files, commands, evidence, limitations, deviations, and final status.
