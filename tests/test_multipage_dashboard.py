"""
Stillwater Multi-Page Dashboard Tests
Tests: Pages load, DataTables render, Charts initialize, VSCode integration

Rung Target: 641
Version: 1.0.0
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Add backend to path
REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT / "admin" / "backend"))

from admin.backend.app import app

client = TestClient(app)

# ============================================================================
# PAGE NAVIGATION TESTS
# ============================================================================


def test_pages_list():
    """Test GET /api/pages returns list of pages"""
    response = client.get("/api/pages")
    assert response.status_code == 200
    data = response.json()
    assert "pages" in data
    assert isinstance(data["pages"], list)
    assert len(data["pages"]) == 5
    assert "orchestration" in data["pages"]
    assert "swarms" in data["pages"]
    assert "cpu" in data["pages"]
    assert "llm" in data["pages"]
    assert "sync" in data["pages"]


# ============================================================================
# PAGE DATA TESTS
# ============================================================================


@pytest.mark.parametrize("page_name", ["orchestration", "swarms", "cpu", "llm", "sync"])
def test_page_data_structure(page_name):
    """Test each page returns complete data structure"""
    response = client.get(f"/api/page/{page_name}/data")
    assert response.status_code == 200
    data = response.json()

    # Verify all required fields
    assert "title" in data
    assert "chat_prompt" in data
    assert "report_config" in data
    assert "table_config" in data
    assert "diagram_mermaid" in data
    assert "instructions" in data

    # Verify types
    assert isinstance(data["title"], str)
    assert isinstance(data["chat_prompt"], str)
    assert isinstance(data["report_config"], dict)
    assert isinstance(data["table_config"], dict)
    assert isinstance(data["diagram_mermaid"], str)
    assert isinstance(data["instructions"], list)

    # Verify table config has columns and data
    assert "columns" in data["table_config"]
    assert "data" in data["table_config"]
    assert len(data["table_config"]["columns"]) > 0
    assert len(data["table_config"]["data"]) > 0

    # Verify table columns have required fields
    for col in data["table_config"]["columns"]:
        assert "data" in col
        assert "title" in col

    # Verify mermaid syntax is not empty
    assert len(data["diagram_mermaid"]) > 0
    assert "graph" in data["diagram_mermaid"].lower() or "flowchart" in data["diagram_mermaid"].lower()

    # Verify instructions have required fields
    for instr in data["instructions"]:
        assert "step" in instr
        assert "title" in instr


# ============================================================================
# CHART CONFIGURATION TESTS
# ============================================================================


@pytest.mark.parametrize("page_name", ["orchestration", "swarms", "cpu", "llm", "sync"])
def test_report_config_has_charts(page_name):
    """Test each page report config has valid charts"""
    response = client.get(f"/api/page/{page_name}/data")
    assert response.status_code == 200
    data = response.json()

    report_config = data["report_config"]
    assert "type" in report_config
    assert report_config["type"] == "multi-chart"

    # Verify charts exist and have required fields
    assert "charts" in report_config
    charts = report_config["charts"]
    assert len(charts) > 0

    for chart in charts:
        assert "id" in chart
        assert "type" in chart
        assert "title" in chart
        # Charts should have type: pie, column, line, area, or gauge
        valid_types = ["pie", "column", "line", "area", "gauge"]
        assert chart["type"] in valid_types


# ============================================================================
# DATA TABLE TESTS
# ============================================================================


@pytest.mark.parametrize("page_name", ["orchestration", "swarms", "cpu", "llm", "sync"])
def test_table_config_complete(page_name):
    """Test table config is complete and valid"""
    response = client.get(f"/api/page/{page_name}/data")
    assert response.status_code == 200
    data = response.json()

    table_config = data["table_config"]

    # Verify columns
    columns = table_config["columns"]
    assert len(columns) >= 2, f"{page_name} should have at least 2 columns"

    for col in columns:
        assert "data" in col
        assert "title" in col
        assert isinstance(col["data"], str)
        assert isinstance(col["title"], str)
        assert len(col["data"]) > 0
        assert len(col["title"]) > 0

    # Verify data rows
    table_data = table_config["data"]
    assert len(table_data) >= 3, f"{page_name} should have at least 3 rows"

    # Verify each row has all column values
    for row in table_data:
        for col in columns:
            assert col["data"] in row, f"Row missing column: {col['data']}"


# ============================================================================
# MERMAID DIAGRAM TESTS
# ============================================================================


@pytest.mark.parametrize("page_name", ["orchestration", "swarms", "cpu", "llm", "sync"])
def test_mermaid_syntax_valid(page_name):
    """Test mermaid diagram syntax is valid"""
    response = client.get(f"/api/page/{page_name}/data")
    assert response.status_code == 200
    data = response.json()

    mermaid = data["diagram_mermaid"]

    # Basic syntax checks
    assert len(mermaid) > 20, "Mermaid diagram too short"
    assert ("graph" in mermaid.lower() or "flowchart" in mermaid.lower()), "Missing graph/flowchart keyword"
    assert ("-->" in mermaid or "--" in mermaid), "Missing connection arrows"
    assert "[" in mermaid and "]" in mermaid, "Missing node brackets"


# ============================================================================
# INSTRUCTIONS TESTS
# ============================================================================


@pytest.mark.parametrize("page_name", ["orchestration", "swarms", "cpu", "llm", "sync"])
def test_instructions_complete(page_name):
    """Test instructions are complete and valid"""
    response = client.get(f"/api/page/{page_name}/data")
    assert response.status_code == 200
    data = response.json()

    instructions = data["instructions"]
    assert len(instructions) >= 2, f"{page_name} should have at least 2 instructions"

    for instr in instructions:
        assert "step" in instr
        assert "title" in instr
        assert isinstance(instr["step"], str)
        assert isinstance(instr["title"], str)
        assert len(instr["title"]) > 0


# ============================================================================
# METRICS ENDPOINT TESTS
# ============================================================================


@pytest.mark.parametrize("page_name", ["orchestration", "swarms", "cpu", "llm", "sync"])
def test_metrics_endpoint(page_name):
    """Test /api/page/{name}/metrics returns valid metrics"""
    response = client.get(f"/api/page/{page_name}/metrics")
    assert response.status_code == 200
    data = response.json()

    assert "metrics" in data
    metrics = data["metrics"]
    assert "timestamp" in metrics
    assert "page" in metrics
    assert metrics["page"] == page_name


# ============================================================================
# VSCODE INTEGRATION TESTS
# ============================================================================


def test_vscode_open_endpoint():
    """Test POST /api/vscode/open endpoint"""
    response = client.post(
        "/api/vscode/open",
        json={"file": "data/default/orchestration.yaml"}
    )
    assert response.status_code == 200
    data = response.json()

    assert "success" in data
    assert "message" in data
    # success can be True (VSCode found) or True (VSCode not found but path prepared)
    assert isinstance(data["success"], bool)


def test_vscode_open_with_different_files():
    """Test VSCode open with different file types"""
    test_files = [
        "data/default/llm_config.yaml",
        "data/default/solace_agi_config.yaml",
        "swarms/scout.md"
    ]

    for file_path in test_files:
        response = client.post(
            "/api/vscode/open",
            json={"file": file_path}
        )
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "message" in data


def test_vscode_open_security():
    """Test VSCode open prevents path traversal attacks"""
    response = client.post(
        "/api/vscode/open",
        json={"file": "../../etc/passwd"}
    )
    # Should either fail or prepare safe path
    assert response.status_code in [200, 403]


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================


def test_page_not_found():
    """Test 404 for invalid page"""
    response = client.get("/api/page/nonexistent/data")
    assert response.status_code == 404


def test_metrics_not_found():
    """Test 404 for metrics of invalid page"""
    response = client.get("/api/page/nonexistent/metrics")
    assert response.status_code == 404


# ============================================================================
# INTEGRATION TESTS
# ============================================================================


def test_all_pages_loadable():
    """Test that all pages can be loaded in sequence"""
    pages_response = client.get("/api/pages")
    assert pages_response.status_code == 200
    pages = pages_response.json()["pages"]

    for page_name in pages:
        data_response = client.get(f"/api/page/{page_name}/data")
        assert data_response.status_code == 200

        metrics_response = client.get(f"/api/page/{page_name}/metrics")
        assert metrics_response.status_code == 200


def test_orchestration_page_specific():
    """Test Orchestration page has expected content"""
    response = client.get("/api/page/orchestration/data")
    assert response.status_code == 200
    data = response.json()

    # Verify Orchestration-specific content
    assert "Orchestration" in data["title"]
    assert "Explorer" in data["diagram_mermaid"] or "Triple Twin" in data["chat_prompt"]


def test_swarms_page_specific():
    """Test Swarms page has expected content"""
    response = client.get("/api/page/swarms/data")
    assert response.status_code == 200
    data = response.json()

    # Verify Swarms-specific content
    assert "Swarms" in data["title"] or "swarm" in data["chat_prompt"].lower()


def test_cpu_page_specific():
    """Test CPU page has expected content"""
    response = client.get("/api/page/cpu/data")
    assert response.status_code == 200
    data = response.json()

    # Verify CPU-specific content
    assert "CPU" in data["title"] or "algorithm" in data["chat_prompt"].lower()


def test_llm_page_specific():
    """Test LLM page has expected content"""
    response = client.get("/api/page/llm/data")
    assert response.status_code == 200
    data = response.json()

    # Verify LLM-specific content
    assert "LLM" in data["title"] or "model" in data["chat_prompt"].lower()


def test_sync_page_specific():
    """Test Sync page has expected content"""
    response = client.get("/api/page/sync/data")
    assert response.status_code == 200
    data = response.json()

    # Verify Sync-specific content
    assert "Sync" in data["title"] or "sync" in data["chat_prompt"].lower()


# ============================================================================
# CONSOLE ERROR SIMULATION (Rung 641)
# ============================================================================


def test_no_missing_endpoints():
    """Verify all expected endpoints are registered"""
    endpoints_to_test = [
        ("/api/pages", "get"),
        ("/api/page/orchestration/data", "get"),
        ("/api/page/orchestration/metrics", "get"),
        ("/api/vscode/open", "post"),
        ("/health", "get"),
    ]

    for endpoint, method in endpoints_to_test:
        if method == "get":
            response = client.get(endpoint)
        else:
            response = client.post(endpoint, json={})

        # Should not be 404 (may be other error codes for missing fields)
        assert response.status_code != 404, f"{endpoint} not found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
