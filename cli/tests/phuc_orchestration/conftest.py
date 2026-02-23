"""
Conftest for phuc_orchestration integration tests.

Auto-skips tests that require a live LLM service (localhost:8080)
when the service is not running. Prevents test suite from hanging.
"""

import socket
import pytest

_LLM_PORTS = [8080, 8788]  # claude-code wrapper, LLM portal


def _is_port_open(host: str, port: int, timeout: float = 1.0) -> bool:
    """Check if a TCP port is accepting connections."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except (ConnectionRefusedError, OSError, TimeoutError):
        return False


def _llm_available() -> bool:
    """Return True if any known LLM service port is accepting connections."""
    return any(_is_port_open("127.0.0.1", port) for port in _LLM_PORTS)


# Cache the result once per session (don't probe every test)
_LLM_UP = None


def pytest_collection_modifyitems(config, items):
    """Auto-skip all tests in this directory when no LLM service is running."""
    global _LLM_UP
    if _LLM_UP is None:
        _LLM_UP = _llm_available()

    if _LLM_UP:
        return  # LLM is running, let all tests execute

    # All phase tests in this directory require a live LLM service
    llm_files = {
        "test_phase_act_solver.py",
        "test_phase_dream_scout.py",
        "test_phase_forecast_grace.py",
        "test_phase_verify_skeptic.py",
    }

    skip_marker = pytest.mark.skip(
        reason="LLM service not running on localhost:8080 or :8788"
    )

    for item in items:
        if item.path.name in llm_files:
            item.add_marker(skip_marker)
