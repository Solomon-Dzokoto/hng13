"""Quick local test to verify API endpoints work correctly."""
import sys
from fastapi.testclient import TestClient
import app

client = TestClient(app.app)

def test_post_create():
    """Test POST /strings creates a string and returns 201"""
    payload = {"value": "Racecar"}
    r = client.post("/strings", json=payload)
    print(f"POST /strings status: {r.status_code}")
    print(f"Response: {r.json()}")
    assert r.status_code == 201, f"Expected 201, got {r.status_code}"
    body = r.json()
    assert body["value"] == "Racecar"
    assert body["properties"]["is_palindrome"] is True
    print("✓ POST /strings works")

def test_duplicate_409():
    """Test duplicate returns 409"""
    payload = {"value": "test123"}
    client.post("/strings", json=payload)
    r = client.post("/strings", json=payload)
    print(f"Duplicate POST status: {r.status_code}")
    assert r.status_code == 409, f"Expected 409, got {r.status_code}"
    print("✓ Duplicate returns 409")

def test_get_specific():
    """Test GET /strings/{value}"""
    payload = {"value": "hello"}
    client.post("/strings", json=payload)
    r = client.get("/strings/hello")
    print(f"GET /strings/hello status: {r.status_code}")
    assert r.status_code == 200
    print("✓ GET specific string works")

def test_missing_value():
    """Test missing value field returns 400"""
    r = client.post("/strings", json={})
    print(f"POST with missing value status: {r.status_code}")
    assert r.status_code == 400, f"Expected 400, got {r.status_code}"
    print("✓ Missing value returns 400")

def test_invalid_type():
    """Test invalid type returns 422"""
    r = client.post("/strings", json={"value": 123})
    print(f"POST with int value status: {r.status_code}")
    assert r.status_code == 422, f"Expected 422, got {r.status_code}"
    print("✓ Invalid type returns 422")

if __name__ == "__main__":
    print("Running local API tests...\n")
    test_post_create()
    test_duplicate_409()
    test_get_specific()
    test_missing_value()
    test_invalid_type()
    print("\n✅ All tests passed!")
