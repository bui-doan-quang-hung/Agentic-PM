import os
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker


test_database_url = os.environ.get("TEST_DATABASE_URL")
if not test_database_url:
    raise RuntimeError(
        "Set TEST_DATABASE_URL to a dedicated disposable PostgreSQL test database; "
        "tests will not fall back to DATABASE_URL"
    )
if not test_database_url.startswith("postgresql+"):
    raise RuntimeError("TEST_DATABASE_URL must use PostgreSQL; SQLite is not supported")

test_admin_engine = create_engine(test_database_url, pool_pre_ping=True)
test_schema_name = f"test_{uuid4().hex}"
with test_admin_engine.begin() as connection:
    connection.execute(text(f'CREATE SCHEMA "{test_schema_name}"'))

isolated_test_url = make_url(test_database_url).update_query_dict(
    {"options": f"-csearch_path={test_schema_name}"}
)
os.environ["DATABASE_URL"] = str(isolated_test_url)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.main import Base, app, engine as app_engine, get_db  # noqa: E402


@pytest.fixture()
def client():
    """Use an isolated PostgreSQL database; never connect to Compose's volume."""
    Base.metadata.drop_all(app_engine)
    Base.metadata.create_all(app_engine)
    TestingSession = sessionmaker(bind=app_engine, expire_on_commit=False)

    def override_get_db():
        with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()

def pytest_sessionfinish(session, exitstatus):
    app_engine.dispose()
    with test_admin_engine.begin() as connection:
        connection.execute(text(f'DROP SCHEMA "{test_schema_name}" CASCADE'))
    test_admin_engine.dispose()
