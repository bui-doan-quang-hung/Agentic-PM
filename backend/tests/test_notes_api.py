from datetime import datetime

import pytest


def create_note(client, title="Demo", content=None, priority="MEDIUM"):
    return client.post(
        "/api/notes",
        json={"title": title, "content": content, "priority": priority},
    )


def test_create_note_defaults_and_timestamps(client):
    response = create_note(client, title=" Demo ", content="text")
    assert response.status_code == 201
    note = response.json()
    assert isinstance(note["id"], int)
    assert note["title"] == "Demo"
    assert note["priority"] == "MEDIUM"
    assert note["status"] == "TODO"
    assert note["content"] == "text"
    assert datetime.fromisoformat(note["created_at"])
    assert datetime.fromisoformat(note["updated_at"])
    assert client.get(f"/api/notes/{note['id']}").json() == note


def test_list_returns_multiple_notes(client):
    first = create_note(client, title="First").json()
    second = create_note(client, title="Second", priority="HIGH").json()
    response = client.get("/api/notes")
    assert response.status_code == 200
    assert [n["id"] for n in response.json()] == [first["id"], second["id"]]
    assert {n["title"] for n in response.json()} == {"First", "Second"}


def test_update_preserves_status_and_creation_timestamp(client):
    original = create_note(client).json()
    assert client.patch(f"/api/notes/{original['id']}/status", json={"status": "DOING"}).status_code == 200
    before = client.get(f"/api/notes/{original['id']}").json()
    response = client.put(
        f"/api/notes/{original['id']}",
        json={"title": "Changed", "content": "new", "priority": "HIGH"},
    )
    assert response.status_code == 200
    updated = response.json()
    assert (updated["title"], updated["content"], updated["priority"]) == ("Changed", "new", "HIGH")
    assert updated["status"] == before["status"] == "DOING"
    assert updated["created_at"] == before["created_at"]
    assert datetime.fromisoformat(updated["updated_at"]) >= datetime.fromisoformat(before["updated_at"])


def test_delete_is_hard_delete(client):
    note = create_note(client).json()
    assert client.delete(f"/api/notes/{note['id']}").status_code == 204
    assert client.get(f"/api/notes/{note['id']}").status_code == 404
    assert client.get("/api/notes").json() == []


@pytest.mark.parametrize("status", ["TODO", "DOING", "DONE"])
def test_all_status_values_are_allowed(client, status):
    note = create_note(client).json()
    response = client.patch(f"/api/notes/{note['id']}/status", json={"status": status})
    assert response.status_code == 200
    assert response.json()["status"] == status
    assert response.json()["created_at"] == note["created_at"]
    assert datetime.fromisoformat(response.json()["updated_at"]) >= datetime.fromisoformat(note["updated_at"])


@pytest.mark.parametrize(
    "payload",
    [
        {"priority": "MEDIUM"},
        {"title": "", "priority": "MEDIUM"},
        {"title": "   ", "priority": "MEDIUM"},
        {"title": "x" * 256, "priority": "MEDIUM"},
        {"title": "bad priority", "priority": "URGENT"},
        {"title": "bad status", "priority": "MEDIUM", "status": "BLOCKED"},
    ],
)
def test_invalid_create_is_rejected_without_mutation(client, payload):
    assert create_note(client).status_code == 201
    before = client.get("/api/notes").json()
    assert client.post("/api/notes", json=payload).status_code == 422
    assert client.get("/api/notes").json() == before


def test_exactly_255_char_title_is_accepted(client):
    response = create_note(client, title="x" * 255)
    assert response.status_code == 201
    assert len(response.json()["title"]) == 255


def test_invalid_update_and_status_do_not_mutate_note(client):
    note = create_note(client).json()
    before = client.get(f"/api/notes/{note['id']}").json()
    bad_update = client.put(
        f"/api/notes/{note['id']}", json={"title": " ", "content": "changed", "priority": "HIGH"}
    )
    bad_status = client.patch(f"/api/notes/{note['id']}/status", json={"status": "INVALID"})
    assert bad_update.status_code == 422
    assert bad_status.status_code == 422
    assert client.get(f"/api/notes/{note['id']}").json() == before


def test_documented_success_not_found_and_validation_codes(client):
    assert create_note(client, title="codes").status_code == 201
    assert client.get("/api/notes").status_code == 200
    assert client.get("/api/notes/99999").status_code == 404
    assert client.put("/api/notes/99999", json={"title": "x", "content": None, "priority": "LOW"}).status_code == 404
    assert client.patch("/api/notes/99999/status", json={"status": "TODO"}).status_code == 404
    assert client.delete("/api/notes/99999").status_code == 404
    assert client.post("/api/notes", json={"title": "", "priority": "LOW"}).status_code == 422


def test_health_checks_database(client):
    assert client.get("/health").json() == {"status": "ok"}
