# Sticky Notes App

A small React + FastAPI + SQLAlchemy app backed by PostgreSQL. PostgreSQL is the source of truth; the browser loads notes from the API and does not persist note data in localStorage.

## Run locally

Requires Docker Desktop with the Linux container engine running and Docker Compose v2.

Copy the example environment file, then set a private local database password in `.env`:

```powershell
Copy-Item .env.example .env
```

`.env` is ignored by Git. Keep real credentials there and do not add it to Git; `.env.example` contains demo values only.

Configure and start the app with:

```powershell
docker compose up --build
```

Open the UI at <http://localhost:5173>. The API is at <http://localhost:8000>; interactive API documentation is at <http://localhost:8000/docs>. PostgreSQL data is kept in the named `postgres_data` volume.

Stop containers while retaining database data with `Ctrl+C`, then `docker compose down`. To deliberately erase the local database, use `docker compose down -v`.

## Verify

Use the UI to create a note (title and priority), edit it, change status, and delete it. Use `/docs` or an HTTP client to verify status codes and validation. Refresh the UI to confirm notes reload from the API. For restart persistence, create a note, run `docker compose restart api frontend`, then fetch it again; keep the `postgres_data` volume.

The detailed contract and AC-1 through AC-10 are in `specs/sticky-note.md`.
