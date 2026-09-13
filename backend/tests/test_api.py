import pytest
from unittest.mock import patch, MagicMock
import os

# Set env vars before importing app
os.environ.setdefault("COHERE_API_KEY", "test-key")
os.environ.setdefault("GROQ_API_KEY", "test-key")

# We need to mock cohere and groq before they're imported
with patch.dict('sys.modules', {
    'cohere': MagicMock(),
    'groq': MagicMock(),
}):
    from fastapi.testclient import TestClient
    from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_empty_content():
    response = client.post("/ingest", json={"type": "note", "content": ""})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_CONTENT"


def test_ingest_invalid_url():
    response = client.post("/ingest", json={"type": "url", "content": "not-a-url"})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "INVALID_URL"


def test_ingest_missing_type():
    response = client.post("/ingest", json={"content": "hello"})
    assert response.status_code == 422  # Pydantic validation


def test_query_empty_question():
    response = client.post("/query", json={"question": ""})
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "EMPTY_QUESTION"


def test_list_items_returns_list():
    response = client.get("/items")
    assert response.status_code == 200
    assert "items" in response.json()


def test_delete_nonexistent_item():
    response = client.delete("/items/nonexistent-id")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
