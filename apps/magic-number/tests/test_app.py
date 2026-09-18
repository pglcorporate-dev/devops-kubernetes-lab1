import pytest
from app import app


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_home_page_returns_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"<html" in response.data


def test_guess_flow_start_and_higher(client):
    first = client.post("/guess", json={"answer": "start"})
    assert first.status_code == 200

    second = client.post("/guess", json={"answer": "higher"})
    assert second.status_code == 200
    assert b"Is it" in second.get_json()["message"].encode("utf-8")


def test_guess_without_json_returns_bad_request(client):
    response = client.post("/guess")
    assert response.status_code == 400
    assert response.get_json()["error"] == "Request body must be valid JSON"
