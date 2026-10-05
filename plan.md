# Sticky Notes App — Implementation Plan

**Readiness:** READY_FOR_BUILD, based on the locked spec and handoff.  
**Scope:** Implement only the requirements in `specs/sticky-note.md`.

## Slices

1. **Local stack:** Docker Compose frontend, API, PostgreSQL services; named PostgreSQL volume; repeatable schema initialization. Maps to AC-7 and AC-10.
2. **Persistence/API:** SQLAlchemy note model, field validation, CRUD/status endpoints, HTTP codes, timestamps. Maps to AC-1, AC-3 through AC-7, and AC-9.
3. **React UI:** Create/edit form, list, status selector, delete action; load data from API on initial render and refresh. Maps to AC-1, AC-2, AC-3, AC-4, AC-5, and AC-8.
4. **Run and verify:** Build and start Compose services, exercise endpoints and UI, inspect PostgreSQL, restart app services while retaining the volume, record evidence. Maps to AC-1 through AC-10.

## Acceptance-Criteria Verification Map

| AC | Implementation / verification evidence |
|---|---|
| AC-1 | POST endpoint returns created model; GET by ID verifies default status, fields, and timestamps. |
| AC-2 | List endpoint returns distinct notes; React list renders each note and status. |
| AC-3 | PUT updates title/content/priority while status and `created_at` remain unchanged; `updated_at` advances. |
| AC-4 | DELETE returns 204; GET returns 404; list and database query show no row. |
| AC-5 | PATCH permits all valid states including direct TODO→DONE; response/GET and timestamps are checked. |
| AC-6 | Invalid/missing/empty/whitespace/overlong title, priority, and status return 422 with no persisted mutation; 255-character title succeeds. |
| AC-7 | Create a note, restart API/frontend only, retain PostgreSQL volume, then GET same ID and compare fields. |
| AC-8 | Create and load a note in React, refresh browser, confirm the same backend-loaded note remains visible; no localStorage persistence. |
| AC-9 | Capture success codes and missing-ID 404 responses for GET/PUT/PATCH/DELETE plus validation 422 responses. |
| AC-10 | Start all services using documented clean-checkout Compose steps; verify API health and frontend availability. |

## Exit Conditions

- Compose build and startup succeed with frontend, API, and PostgreSQL healthy/reachable.
- Every acceptance criterion is exercised; no criterion is marked PASS without direct evidence.
- Any implementation failures are fixed and re-verified without changing the spec.
- `delivery-report.md` records commands, results, evidence, limitations, deviations, and final status.
