import pytest
from fastapi.testclient import TestClient
from stage_1 import app


client = TestClient(app.app)


def test_create_and_get_and_delete_string():
    payload = {"value": "Racecar"}
    r = client.post("/strings", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["value"] == "Racecar"
    assert body["properties"]["is_palindrome"] is True

    # GET
    r2 = client.get("/strings/Racecar")
    assert r2.status_code == 200
    assert r2.json()["value"] == "Racecar"

    # Duplicate should be conflict
    r3 = client.post("/strings", json=payload)
    assert r3.status_code == 409

    # Delete
    r4 = client.delete("/strings/Racecar")
    assert r4.status_code == 204

    # Now not found
    r5 = client.get("/strings/Racecar")
    assert r5.status_code == 404


def test_list_and_filters_and_nl():
    # create several strings
    samples = [
        "a",
        "level",
        "hello world",
        "abcba",
        "this is a longer string",
    ]
    for s in samples:
        client.post("/strings", json={"value": s})

    r = client.get("/strings", params={"is_palindrome": "true"})
    assert r.status_code == 200
    data = r.json()
    assert data["count"] >= 2

    r2 = client.get("/strings", params={"min_length": 5, "max_length": 20})
    assert r2.status_code == 200

    r3 = client.get("/strings/filter-by-natural-language", params={"query": "all single word palindromic strings"})
    assert r3.status_code == 200
    parsed = r3.json()["interpreted_query"]["parsed_filters"]
    assert parsed.get("word_count") == 1
    assert parsed.get("is_palindrome") is True
