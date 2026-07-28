"""
API tests. The OpenAI call itself is mocked out so these run offline
without an API key - useful for CI, and for anyone cloning the repo to
verify things work before wiring up a real key.
"""

from unittest.mock import patch

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_chat_rejects_empty_messages():
    resp = client.post("/api/chat", json={"messages": []})
    assert resp.status_code == 400


@patch("app.main.get_reply")
def test_chat_happy_path(mock_get_reply):
    mock_get_reply.return_value = ("Your order ships tomorrow!", ["get_order_status"])

    resp = client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "content": "Where's my order ord-1001?"}]},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"] == "Your order ships tomorrow!"
    assert body["used_tools"] == ["get_order_status"]
