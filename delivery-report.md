# Sticky Notes App — Delivery Report

## Final Status

**READY_FOR_REVIEW** — AC-1 through AC-10 are PASS. AC-2 and AC-8 passed through reviewer-performed manual browser verification. Automated/API/container checks passed, and the previously reported Vite dependency vulnerability was fixed and re-audited.

## Implementation Summary

- Implemented a React note form/list with create, edit, status change, and delete controls.
- Implemented FastAPI/SQLAlchemy endpoints and the locked validation, timestamp, and status rules.
- Added PostgreSQL 16 in Docker Compose with a named postgres_data volume; schema is initialized repeatably on API startup.
- Frontend loads notes from the API at startup; note data is not stored in localStorage.
- Database credentials are supplied through ignored `.env`; `.env.example` contains demo values only.
- Added Compose startup and verification instructions in README.md.
- Replaced the stale plan with build slices and AC mapping in plan.md.
- Updated Vite from 6.3.5 to 6.4.3 to resolve the high-severity advisory found during audit; `npm audit` now reports zero vulnerabilities.

## Project Structure

```text
backend/
  app/main.py
  Dockerfile
  requirements.txt
  .dockerignore
frontend/
  src/App.jsx
  src/main.jsx
  src/style.css
  Dockerfile
  package.json
  package-lock.json
  vite.config.js
  .dockerignore
docker-compose.yml
README.md
plan.md
delivery-report.md
```

## Files Changed / Created

- `.gitignore`
- `.env.example`
- `docker-compose.yml`
- `backend/.dockerignore`
- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/app/__init__.py`
- `backend/app/main.py`
- `frontend/.dockerignore`
- `frontend/Dockerfile`
- `frontend/index.html`
- `frontend/package.json`
- `frontend/package-lock.json`
- `frontend/vite.config.js`
- `frontend/src/main.jsx`
- `frontend/src/App.jsx`
- `frontend/src/style.css`
- `README.md`
- `plan.md`
- `delivery-report.md`

The Git repository is initialized in the project root; no commit or push has been performed.

## Commands Used

- `docker compose up --build -d`
- `docker compose up --build -d api` (rebuild after enforcing TODO-only initial status)
- `docker compose up --build -d frontend` (rebuild after Vite update)
- `docker compose config --quiet`
- `docker compose ps`
- `docker compose restart api frontend`
- `docker compose exec -T db psql -U sticky_notes -d sticky_notes -c 'SELECT id,title,priority,status,created_at,updated_at FROM sticky_notes ORDER BY id;'`
- `docker compose logs --tail 8 api frontend db`
- PowerShell `System.Net.Http.HttpClient` requests to exercise create/read/update/status/delete/validation endpoints and capture response codes.
- PowerShell `Invoke-WebRequest` requests to `/`, `/src/App.jsx`, and `/health`.
- `npm install vite@6.4.3 --save-exact`
- `npm audit --json`

## Verification Summary

- `docker compose up --build -d` built the Python and Node images and started all three services.
- `docker compose ps` showed API and frontend running and PostgreSQL healthy.
- `GET /health` returned `200` with `{"status":"ok"}`.
- Frontend `/` and transformed `/src/App.jsx` each returned `200`; Vite's transformed module included the React JSX runtime.
- API checks ran against the Compose stack and its PostgreSQL database. A separate PostgreSQL 17 instance was also used for an initial local API pass; final acceptance evidence below is from Compose unless noted.
- Follow-up verification confirmed POST with supplied status `DOING` returns `422` without adding a row; omitted status still returns `201` with `TODO`. A final note was patched to `DONE`; PostgreSQL showed `created_at` `04:56:01.147483+00` and later `updated_at` `04:56:01.175135+00`.
- Repeated GETs of the final note one second apart returned the same `updated_at`, confirming reads do not advance it. `docker compose config --quiet` also completed successfully.
- **Automated verification (agent):** Compose build/start, API response/status checks, SQL queries against PostgreSQL, restart persistence, timestamp behavior, frontend HTTP/module checks, and dependency audit.
- **Manual verification (reviewer):** Reviewer opened `http://localhost:5173`, confirmed sticky notes loaded and displayed (AC-2 PASS), then created a note and refreshed the browser, confirming it remained visible (AC-8 PASS). These browser checks were performed by the reviewer, not by the agent.
- After updating Vite to 6.4.3, `npm audit --json` reported zero vulnerabilities; Docker rebuild output also reported zero vulnerabilities from `npm ci`.

## Acceptance Criteria

| AC | Result | Evidence |
|---|---|---|
| **AC-1 Create** | **PASS** | Compose `POST /api/notes` returned `201`; returned integer ID `1`, title `Compose Demo`, priority `MEDIUM`, default status `TODO`, and non-null timestamps. `GET /api/notes/1` returned `200` with the same title. A post-rebuild smoke test also confirmed omitted status creates `TODO`; supplying `DOING` on create returns `422` without mutation. |
| **AC-2 Read/list** | **PASS** | **Automated:** `GET /api/notes` returned `200` and contained both distinct created IDs; frontend root and JSX module returned `200` and JSX transformed successfully. **Manual reviewer verification:** opened `http://localhost:5173` and confirmed sticky notes loaded and displayed correctly. |
| **AC-3 Edit** | **PASS** | `PUT /api/notes/1` returned `200`; title/content/priority changed, status remained `TODO`, `created_at` remained identical, and `updated_at` advanced. |
| **AC-4 Delete** | **PASS** | `DELETE /api/notes/1` returned `204`; subsequent GET returned `404`; list and final direct PostgreSQL query contained no ID `1`. |
| **AC-5 Status** | **PASS** | PATCH requests setting `DONE`, `DOING`, then `TODO` each returned `200` and the requested status. This included the direct `TODO`→`DONE` transition. `created_at` stayed unchanged and `updated_at` advanced for each change. |
| **AC-6 Validation** | **PASS** | Missing title, empty title, whitespace-only title, 256-character title, invalid priority, invalid create status, and invalid PATCH status each returned `422`. The invalid PATCH left status and `updated_at` unchanged; invalid creates did not increase row count. A 255-character title returned `201` and was stored with length 255. |
| **AC-7 PostgreSQL persistence** | **PASS** | Created ID `4` (`Persist across app restart`), ran `docker compose restart api frontend` without removing the volume, then GET returned `200` with the same ID, title, and `created_at`. Direct query in the Compose PostgreSQL container showed ID `4` and its persisted fields. |
| **AC-8 Refresh persistence** | **PASS** | **Automated:** React fetches notes from `GET /api/notes` on initial render and the implementation does not use localStorage for persistence. **Manual reviewer verification:** created a note, refreshed the browser, and confirmed the note remained visible. The agent did not run a browser test. |
| **AC-9 API codes** | **PASS** | Observed POST `201`, list/get/update/status `200`, delete `204`, invalid values `422`, and missing-ID GET/PUT/PATCH/DELETE all `404`. |
| **AC-10 Local run** | **PASS** | From the new workspace, `docker compose up --build -d` created the named volume, initialized PostgreSQL/schema, and started frontend/API/database. `docker compose ps` reported DB healthy and both app services running; API health and frontend root returned `200`. |

## Known Limitations

- The UI runs Vite's development server in Compose, suitable for this local demo rather than production hosting.

## Scope Deviations

None. No authentication, search/filter, drag and drop, notifications, AI, uploads, multiple-user support, or cloud deployment were added.

## Review Notes

The app remains running at <http://localhost:5173>; API at <http://localhost:8000>. Preserve the `postgres_data` volume to retain demo notes. `docker compose down -v` deletes the demo database.

