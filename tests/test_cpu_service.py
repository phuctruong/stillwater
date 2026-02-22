"""Tests for CPU Service (admin/services/cpu_service.py).

Covers:
- Health endpoint
- Hash computation (SHA-256, SHA-512, HMAC-SHA256)
- Invalid algorithm rejection
- Rung validation at all three rungs
- Gap reporting
- Exact arithmetic (add, subtract, multiply, divide, compare, modulo)
- Division by zero / modulo by zero
- Service info endpoint
"""

import hashlib
import hmac
import pytest
from fastapi.testclient import TestClient

from admin.services.cpu_service import app

client = TestClient(app)


# ===== Health =====

def test_health_returns_ok():
    resp = client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"

def test_health_has_service_id():
    resp = client.get("/api/health")
    assert resp.json()["service_id"] == "cpu-service"

def test_health_has_service_type():
    resp = client.get("/api/health")
    assert resp.json()["service_type"] == "cpu"

def test_health_has_version():
    resp = client.get("/api/health")
    assert "version" in resp.json()


# ===== Service Info =====

def test_service_info_returns_port():
    resp = client.get("/api/service-info")
    assert resp.status_code == 200
    data = resp.json()
    assert data["port"] == 8792

def test_service_info_has_name():
    resp = client.get("/api/service-info")
    assert "CPU Service" in resp.json()["name"]

def test_service_info_type_is_cpu():
    resp = client.get("/api/service-info")
    assert resp.json()["service_type"] == "cpu"


# ===== Hash: SHA-256 =====

def test_hash_sha256_known_input():
    resp = client.post("/api/cpu/hash", json={"data": "hello", "algorithm": "sha256"})
    assert resp.status_code == 200
    expected = hashlib.sha256(b"hello").hexdigest()
    assert resp.json()["hash"] == expected

def test_hash_sha256_input_length():
    resp = client.post("/api/cpu/hash", json={"data": "hello", "algorithm": "sha256"})
    assert resp.json()["input_length"] == 5

def test_hash_sha256_algorithm_in_response():
    resp = client.post("/api/cpu/hash", json={"data": "hello", "algorithm": "sha256"})
    assert resp.json()["algorithm"] == "sha256"

def test_hash_sha256_empty_string():
    resp = client.post("/api/cpu/hash", json={"data": "", "algorithm": "sha256"})
    assert resp.status_code == 200
    expected = hashlib.sha256(b"").hexdigest()
    assert resp.json()["hash"] == expected


# ===== Hash: SHA-512 =====

def test_hash_sha512_known_input():
    resp = client.post("/api/cpu/hash", json={"data": "stillwater", "algorithm": "sha512"})
    assert resp.status_code == 200
    expected = hashlib.sha512(b"stillwater").hexdigest()
    assert resp.json()["hash"] == expected

def test_hash_sha512_length_128_chars():
    resp = client.post("/api/cpu/hash", json={"data": "x", "algorithm": "sha512"})
    assert len(resp.json()["hash"]) == 128


# ===== Hash: HMAC-SHA256 =====

def test_hash_hmac_sha256():
    resp = client.post("/api/cpu/hash", json={
        "data": "message",
        "algorithm": "sha256",
        "hmac_key": "secret",
    })
    assert resp.status_code == 200
    expected = hmac.new(b"secret", b"message", hashlib.sha256).hexdigest()
    assert resp.json()["hash"] == expected

def test_hash_hmac_sha256_differs_from_plain():
    plain = client.post("/api/cpu/hash", json={"data": "msg", "algorithm": "sha256"})
    keyed = client.post("/api/cpu/hash", json={
        "data": "msg",
        "algorithm": "sha256",
        "hmac_key": "key",
    })
    assert plain.json()["hash"] != keyed.json()["hash"]


# ===== Hash: Invalid Algorithm =====

def test_hash_invalid_algorithm_rejected():
    resp = client.post("/api/cpu/hash", json={"data": "x", "algorithm": "sha1"})
    assert resp.status_code == 422  # Pydantic validation error


# ===== Rung Validation: Rung 641 =====

def test_rung_641_passes_with_tests_and_artifacts():
    resp = client.post("/api/cpu/validate-rung", json={
        "claimed_rung": 641,
        "evidence_artifacts": ["tests.json"],
        "has_tests": True,
        "has_red_green": False,
        "has_security_review": False,
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["valid"] is True
    assert data["achieved_rung"] == 641

def test_rung_641_fails_without_tests():
    resp = client.post("/api/cpu/validate-rung", json={
        "claimed_rung": 641,
        "evidence_artifacts": ["tests.json"],
        "has_tests": False,
    })
    data = resp.json()
    assert data["valid"] is False
    assert any("No tests" in g for g in data["gaps"])

def test_rung_641_fails_without_artifacts():
    resp = client.post("/api/cpu/validate-rung", json={
        "claimed_rung": 641,
        "evidence_artifacts": [],
        "has_tests": True,
    })
    data = resp.json()
    assert data["valid"] is False
    assert any("artifact" in g.lower() for g in data["gaps"])


# ===== Rung Validation: Rung 274177 =====

def test_rung_274177_requires_red_green():
    resp = client.post("/api/cpu/validate-rung", json={
        "claimed_rung": 274177,
        "evidence_artifacts": ["tests.json"],
        "has_tests": True,
        "has_red_green": True,
    })
    data = resp.json()
    assert data["valid"] is True
    assert data["achieved_rung"] == 274177

def test_rung_274177_fails_without_red_green():
    resp = client.post("/api/cpu/validate-rung", json={
        "claimed_rung": 274177,
        "evidence_artifacts": ["tests.json"],
        "has_tests": True,
        "has_red_green": False,
    })
    data = resp.json()
    assert data["valid"] is False
    assert any("red-green" in g.lower() for g in data["gaps"])


# ===== Rung Validation: Rung 65537 =====

def test_rung_65537_requires_security_review():
    resp = client.post("/api/cpu/validate-rung", json={
        "claimed_rung": 65537,
        "evidence_artifacts": ["tests.json"],
        "has_tests": True,
        "has_red_green": True,
        "has_security_review": True,
    })
    data = resp.json()
    assert data["valid"] is True
    assert data["achieved_rung"] == 65537

def test_rung_65537_fails_without_security_review():
    resp = client.post("/api/cpu/validate-rung", json={
        "claimed_rung": 65537,
        "evidence_artifacts": ["tests.json"],
        "has_tests": True,
        "has_red_green": True,
        "has_security_review": False,
    })
    data = resp.json()
    assert data["valid"] is False
    assert any("security" in g.lower() for g in data["gaps"])

def test_rung_invalid_claimed_rung_returns_not_valid():
    resp = client.post("/api/cpu/validate-rung", json={
        "claimed_rung": 9999,
        "evidence_artifacts": ["tests.json"],
        "has_tests": True,
        "has_red_green": True,
        "has_security_review": True,
    })
    data = resp.json()
    assert data["valid"] is False


# ===== Math: Exact Arithmetic =====

def test_math_add_integers():
    resp = client.post("/api/cpu/math", json={
        "operation": "add",
        "operand_a": "3",
        "operand_b": "4",
    })
    assert resp.status_code == 200
    data = resp.json()
    assert data["result"] == "7"
    assert data["exact"] is True

def test_math_add_fractions_exact():
    resp = client.post("/api/cpu/math", json={
        "operation": "add",
        "operand_a": "1/3",
        "operand_b": "1/6",
    })
    data = resp.json()
    assert data["result"] == "1/2"
    assert data["exact"] is True

def test_math_subtract():
    resp = client.post("/api/cpu/math", json={
        "operation": "subtract",
        "operand_a": "10",
        "operand_b": "3",
    })
    assert resp.json()["result"] == "7"

def test_math_multiply_fractions():
    resp = client.post("/api/cpu/math", json={
        "operation": "multiply",
        "operand_a": "2/3",
        "operand_b": "3/4",
    })
    assert resp.json()["result"] == "1/2"

def test_math_divide_exact():
    resp = client.post("/api/cpu/math", json={
        "operation": "divide",
        "operand_a": "7",
        "operand_b": "2",
    })
    data = resp.json()
    assert data["result"] == "7/2"
    assert data["exact"] is True

def test_math_divide_by_zero():
    resp = client.post("/api/cpu/math", json={
        "operation": "divide",
        "operand_a": "5",
        "operand_b": "0",
    })
    data = resp.json()
    assert "ERROR" in data["result"]
    assert data["exact"] is False

def test_math_compare_greater():
    resp = client.post("/api/cpu/math", json={
        "operation": "compare",
        "operand_a": "3",
        "operand_b": "2",
    })
    assert resp.json()["result"] == "1"

def test_math_compare_equal():
    resp = client.post("/api/cpu/math", json={
        "operation": "compare",
        "operand_a": "5",
        "operand_b": "5",
    })
    assert resp.json()["result"] == "0"

def test_math_compare_less():
    resp = client.post("/api/cpu/math", json={
        "operation": "compare",
        "operand_a": "1",
        "operand_b": "2",
    })
    assert resp.json()["result"] == "-1"

def test_math_modulo():
    resp = client.post("/api/cpu/math", json={
        "operation": "modulo",
        "operand_a": "10",
        "operand_b": "3",
    })
    assert resp.json()["result"] == "1"

def test_math_modulo_by_zero():
    resp = client.post("/api/cpu/math", json={
        "operation": "modulo",
        "operand_a": "5",
        "operand_b": "0",
    })
    data = resp.json()
    assert "ERROR" in data["result"]
    assert data["exact"] is False

def test_math_invalid_operation_rejected():
    resp = client.post("/api/cpu/math", json={
        "operation": "power",
        "operand_a": "2",
        "operand_b": "3",
    })
    assert resp.status_code == 422

def test_math_operation_in_response():
    resp = client.post("/api/cpu/math", json={
        "operation": "add",
        "operand_a": "1",
        "operand_b": "1",
    })
    assert resp.json()["operation"] == "add"
