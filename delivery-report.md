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

## Improvement Addendum — Documentation, Tests, and CI

### Automated Test Results

- **Command:** `python -m pytest -q` (working directory `backend`), with
  `DATABASE_URL` and `TEST_DATABASE_URL` pointing to an isolated PostgreSQL 16
  test container on local port 55433.
- **Result for this addendum:** NOT VERIFIED. The host has Python 3.10 but the
  required packages were not installed; PyPI DNS failed during installation.
  A disposable test-only PostgreSQL container was started, but Docker Desktop
  later began returning HTTP 500 on engine ping before the test command could
  complete. It was not the app's `postgres_data` volume and no Compose service
  was stopped or removed.
- **Test suite added:** 17 pytest cases (including parameterized inputs) using
  FastAPI TestClient and an isolated UUID-named PostgreSQL schema; teardown
  drops only that schema. Coverage includes create and
  default TODO, listing, field updates and timestamp invariants, hard delete,
  all statuses, invalid inputs without mutation, 255-character title boundary,
  API status codes, and database health.
- **AC mapping:** AC-1, AC-2 API listing, AC-3, AC-4, AC-5, AC-6, AC-9 API
  codes, and health portion of AC-10 have automated test cases. AC-7 restart
  persistence remains an integration/manual check. AC-2 UI, AC-8 browser
  refresh, full AC-9 browser/API walkthrough, and full AC-10 Compose startup
  remain as previously recorded manual/container evidence. No test result in
  this addendum is reported PASS without execution evidence.

### Frontend Verification

- `npm ci`: PASS. Clean installation added 65 packages and reported zero
  vulnerabilities.
- `npm audit --audit-level=high`: was included in the same command chain but
  did not complete because Vite build stalled first.
- `npm run build`: NOT VERIFIED. Both host and isolated Linux attempts stalled
  at Vite's `transforming…` stage while esbuild consumed excessive CPU/memory.
  The process was stopped; no build PASS is claimed.
- E2E: E2E_NOT_AVAILABLE. No browser automation infrastructure is configured;
  retain the existing manual reviewer evidence for AC-2 and AC-8.

### CI

- **Workflow:** `.github/workflows/ci.yml`
- **Triggers:** push to `main` and pull requests targeting `main`.
- **Backend:** Python 3.12, ephemeral PostgreSQL 16 health-checked service,
  requirements install, pytest.
- **Frontend:** Node 22, `npm ci`, Vite production build, `npm audit
  --audit-level=high`.
- **Local validation:** workflow content reviewed; GitHub Actions schema/runtime
  not validated locally.
- **Remote status:** CI_CONFIGURED_NOT_REMOTE_VERIFIED. No GitHub Actions run
  evidence exists yet.

### Security / Repository Check

- `.env` is ignored and not tracked (`git ls-files .env` returned no path).
- `.venv/`, `frontend/node_modules/`, `frontend/dist/`, `__pycache__/`, and
  `*.pyc` are ignored.
- A repository scan for common private-key, GitHub/GitLab token, AWS key, and
  credential assignment patterns returned no matches in tracked source/config
  candidates. `.env.example` contains demo placeholders only. This is a
  heuristic scan, not a guarantee that arbitrary secrets are absent.
- No credentials were added to CI; its PostgreSQL password is ephemeral and
  exists only inside the service job.

### Files Added or Updated by This Addendum

- `README.md`: agentic workflow, architecture, artifacts, local/testing
  instructions, AC summary, CI description.
- `backend/requirements.txt`: pytest and HTTPX test dependencies.
- `backend/tests/conftest.py`, `backend/tests/test_notes_api.py`: isolated
  PostgreSQL-backed API tests.
- `frontend/package.json`: production build and currently unconfigured E2E
  script declaration.
- `.github/workflows/ci.yml`: backend, frontend, and dependency audit jobs.
- `delivery-report.md`: this evidence addendum.

No locked specification, API behavior, product scope, or existing database
volume was changed. The GitHub workflow has not been run remotely, and no
commit or push was performed.

## Final Verification Retry — 2026-10-05

### Backend

- `py -3 -m pip install -r backend/requirements.txt`: **PASS**. Pinned project
  dependencies installed on the host. Pip reported an unrelated globally
  installed `pytest-asyncio` constraint warning; this test suite is synchronous.
- `py -3 -m pytest backend/tests -v`: **NOT RUN**. Docker Desktop's Linux
  engine returned HTTP 500. The previously created test port (55433) accepted
  TCP but closed the PostgreSQL handshake, so it was not a usable database.
  Pytest was not pointed at either port 55432 (unknown owner) or the Compose
  database. No backend test is marked PASS based on the earlier acceptance
  report; the 17 newly added cases remain unverified.

### Frontend

- `npm ci`: **PASS** on the host; 64 packages installed and npm reported zero
  vulnerabilities.
- `npm run build`: **NOT VERIFIED**. It first failed because Vite was absent
  before `npm ci`; after installation, Vite repeatedly stalled at
  `transforming…`, with Node reaching about 1.5 GB of memory. Trace logging
  showed source, JSX and CSS modules transform, then the regular bundle hangs
  when Rollup includes the `react-dom/client` CommonJS dependency graph.
- Isolated checks: esbuild JSX transform passed; PostCSS parsed the stylesheet;
  an externalized diagnostic build completed in under a second. That output
  omits React runtime dependencies and is **not** a production build/pass.
- No dependency or shipping configuration was changed to mask the issue. The
  diagnostic `frontend/dist` output is ignored and was not staged; the
  environment rejected its removal command.
- `npm audit --audit-level=high`: not run as a separate command. `npm ci`'s
  bundled audit reported zero vulnerabilities.

### Compose and GitHub Actions

- `docker compose config --quiet`: **PASS**.
- Runtime build/start: **NOT VERIFIED**. Docker Desktop engine calls returned
  HTTP 500; no Compose services were stopped and no volume was removed.
- `.github/workflows/ci.yml` static review: `main` push/PR triggers; read-only
  contents permission; PostgreSQL 16 health-checked service; ephemeral CI-only
  database credentials; Python 3.12; backend command
  `python -m pytest backend/tests -v`; Node 22; `npm ci`; `npm run build`; and
  `npm audit --audit-level=high`. The backend command matches the local pytest
  target, but neither pytest nor build has a successful local run yet.
- Remote result: **CI_CONFIGURED_NOT_REMOTE_VERIFIED**. No GitHub Actions run
  evidence exists.

### Final Repository Checks

- `git diff --check`: **PASS** (Git emitted only line-ending conversion notices).
- `.env`: ignored and not tracked/staged. `frontend/node_modules`,
  `frontend/dist`, and Python `__pycache__`/`.pyc` are ignored and not staged.
- Common secret-pattern scan found no matching private key/token/key/password
  assignments in repository source/config candidates; local `.env` was excluded
  from scan output and is ignored. This is heuristic, not a proof of absence.
- `git status` contains only the expected README, backend test/dependency,
  frontend build-script, workflow and delivery-report changes. No commit/push.

### AC Status for This Retry

Newly added automated tests were not run, so they do not count as PASS.
Previously recorded evidence is kept distinct below:

| AC | Status | Evidence basis |
|---|---|---|
| AC-1 | PARTIAL | Prior API verification is documented; new pytest case not run. |
| AC-2 | MANUAL_PASS | Prior reviewer browser check; new pytest case not run. |
| AC-3 | PARTIAL | Prior API check documented; new pytest case not run. |
| AC-4 | PARTIAL | Prior API/database check documented; new pytest case not run. |
| AC-5 | PARTIAL | Prior status API check documented; new pytest case not run. |
| AC-6 | PARTIAL | Prior validation checks documented; new pytest case not run. |
| AC-7 | PARTIAL | Prior PostgreSQL restart/retention evidence is recorded, but it was not rerun and the new pytest suite did not run. |
| AC-8 | MANUAL_PASS | Prior reviewer refresh check; no E2E added. |
| AC-9 | PARTIAL | Prior status-code checks documented; new pytest case not run. |
| AC-10 | PARTIAL | Prior Compose runtime evidence exists; current runtime could not be rechecked. |

**Readiness:** `NOT_READY_FOR_COMMIT`. The new backend suite has not actually
passed and the frontend production bundle has not been produced. Current
blockers are Docker Desktop engine/PostgreSQL test service availability and the
Vite/Rollup `react-dom/client` bundling stall. No commit, push, image publish,
database-volume deletion, or product-scope change occurred.

## Blocker Resolution Follow-up — 2026-10-05

### Frontend

- Root cause evidence: React and React DOM were both 19.1.0 with one deduped
  installation; source imports had no cycle; the Vite React plugin config was
  standard. Vite 5.4.14 and Vite 6.4.3 repeatedly stalled in Rollup while
  bundling `react-dom/client`, including after a clean `npm ci`. A diagnostic
  Vite 8.3.2 build using Rolldown completed the same production bundle in
  537 ms. This isolates the stall to the Rollup bundling path in this Windows
  environment.
- Minimal tooling fix: aligned Vite and its React plugin to exact compatible
  versions, `vite@8.3.2` and `@vitejs/plugin-react@6.1.1`. No React runtime
  dependency was externalized and application code was unchanged.
- After the lockfile update: `npm ci` **PASS**; `npm run build` **PASS**;
  generated `frontend/dist/index.html` and JS/CSS assets (16 modules, React
  included); `npm audit --audit-level=high` **PASS**, zero vulnerabilities.

### Backend

- Docker Desktop Linux engine still returns HTTP 500. Compose configuration
  validation passes, but Docker runtime verification remains unavailable.
- The listener on port 55432 was confirmed as the existing developer database
  using `D:/sticky-notes-pgdata`; it was not used or modified. A separate
  PostgreSQL 17 cluster and `sticky_notes_test` database were created under the
  OS temporary directory on port 55434 with local trust authentication and no
  reusable credential. Pytest's UUID-named schema isolated test tables within
  that database. The temporary server was stopped after testing.
- The requested root-level pytest command initially exposed a test harness
  import-path error (`backend/app` was not on `sys.path`). `backend/tests/conftest.py`
  now adds the backend directory for test imports. The full command
  `py -3 -m pytest backend/tests -v` then executed **17 tests, 17 passed,
  0 failed** in 0.73 s. CI retains the equivalent
  `python -m pytest backend/tests -v` command and its isolated PostgreSQL
  service/database.

### Final checks

- `docker compose config --quiet`: **PASS**. Docker service build/start remains
  unverified due to the engine error.
- `.github/workflows/ci.yml`: static configuration reviewed for PostgreSQL
  service and test URL, Python 3.12, Node 22, `npm ci`, `npm run build`, and
  high severity npm audit. Remote result remains
  `CI_CONFIGURED_NOT_REMOTE_VERIFIED`.
- `git diff --check`: **PASS** (only line-ending conversion notices).
  `.env` is ignored and not tracked; no files are staged. `npm audit` reported
  zero vulnerabilities. `specs/sticky-note.md` and API/application behavior
  are unchanged. The existing PostgreSQL database/volume was not touched.
- Docker runtime build/start remains unverified because Docker Desktop's Linux
  engine returns HTTP 500. The requested Compose configuration check passes.
- Overall status: **READY_FOR_COMMIT** against the stated local readiness gate:
  all 17 backend tests passed against isolated PostgreSQL, the clean frontend
  install and production bundle passed, Compose configuration passed, and
  security checks passed. GitHub Actions remains
  `CI_CONFIGURED_NOT_REMOTE_VERIFIED`. No commit or push was performed.

