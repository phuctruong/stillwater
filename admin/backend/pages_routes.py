"""
Stillwater Multi-Page Homepage — API Routes

Provides endpoints for:
- Page navigation and structure
- Page-specific metrics and sample data
- VSCode integration (open files in editor)

Rung Target: 641 (Local Correctness)
Version: 1.0.0
"""

import json
import logging
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# Router for page routes
router = APIRouter(prefix="/api", tags=["pages"])

# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class PageDataResponse(BaseModel):
    """Response for a single page's data"""
    title: str
    chat_prompt: str
    report_config: Dict[str, Any]
    table_config: Dict[str, Any]
    diagram_mermaid: str
    instructions: List[Dict[str, str]]


class MetricsResponse(BaseModel):
    """Current metrics for a page"""
    metrics: Dict[str, Any]


class VSCodeRequest(BaseModel):
    """Request to open a file in VSCode"""
    file: str = Field(..., description="File path to open (relative to repo root)")


class VSCodeResponse(BaseModel):
    """Response from VSCode open request"""
    success: bool
    message: str


class PagesListResponse(BaseModel):
    """List of all available pages"""
    pages: List[str]


# ============================================================================
# SAMPLE DATA & PAGE DEFINITIONS
# ============================================================================

PAGE_DEFINITIONS = {
    "orchestration": {
        "title": "Orchestration",
        "chat_prompt": "Ask orchestration questions or run commands on the Triple Twin (Explorer, Builder, Arbiter)",
        "report_config": {
            "type": "multi-chart",
            "charts": [
                {
                    "id": "rung-progress",
                    "type": "pie",
                    "title": "Rung Distribution",
                    "data": [
                        {"name": "Rung 641", "value": 45},
                        {"name": "Rung 274177", "value": 35},
                        {"name": "Rung 65537", "value": 20}
                    ]
                },
                {
                    "id": "recent-tasks",
                    "type": "column",
                    "title": "Recent Tasks (Last 7 Days)",
                    "data": [
                        {"date": "Mon", "tasks": 8},
                        {"date": "Tue", "tasks": 12},
                        {"date": "Wed", "tasks": 10},
                        {"date": "Thu", "tasks": 15},
                        {"date": "Fri", "tasks": 7},
                        {"date": "Sat", "tasks": 3},
                        {"date": "Sun", "tasks": 5}
                    ]
                },
                {
                    "id": "triple-twin-status",
                    "type": "gauge",
                    "title": "System Health",
                    "value": 87
                }
            ]
        },
        "table_config": {
            "columns": [
                {"data": "role", "title": "Role"},
                {"data": "model", "title": "Model"},
                {"data": "status", "title": "Status"},
                {"data": "last_run", "title": "Last Run"}
            ],
            "data": [
                {"role": "Explorer", "model": "haiku", "status": "Ready", "last_run": "2 min ago"},
                {"role": "Builder", "model": "sonnet", "status": "Running", "last_run": "now"},
                {"role": "Arbiter", "model": "sonnet", "status": "Ready", "last_run": "5 min ago"}
            ]
        },
        "diagram_mermaid": """graph TD
    A["🔍 Explorer<br/>haiku<br/>Status: Ready"]
    B["🔨 Builder<br/>sonnet<br/>Status: Running"]
    C["⚖️ Arbiter<br/>sonnet<br/>Status: Ready"]

    A -->|Explores| B
    B -->|Builds| C
    C -->|Verifies| A

    style A fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    style B fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style C fill:#f3e5f5,stroke:#4a148c,stroke-width:2px""",
        "instructions": [
            {
                "step": "1",
                "title": "Click a node in the diagram",
                "description": "View details for Explorer, Builder, or Arbiter"
            },
            {
                "step": "2",
                "title": "Edit orchestration config",
                "file": "data/default/orchestration.yaml",
                "button": "Open in VSCode"
            },
            {
                "step": "3",
                "title": "Run orchestration",
                "command": "stillwater orchestration run"
            }
        ]
    },
    "swarms": {
        "title": "Swarm Nodes",
        "chat_prompt": "Ask a swarm to do something: coder, planner, skeptic, scout, mathematician, writer",
        "report_config": {
            "type": "multi-chart",
            "charts": [
                {
                    "id": "success-rates",
                    "type": "column",
                    "title": "Success Rate by Swarm (%)",
                    "data": [
                        {"swarm": "Coder", "rate": 92},
                        {"swarm": "Planner", "rate": 87},
                        {"swarm": "Scout", "rate": 94},
                        {"swarm": "Skeptic", "rate": 89}
                    ]
                },
                {
                    "id": "token-usage",
                    "type": "area",
                    "title": "Token Usage (Last 7 Days)",
                    "data": [
                        {"date": "Mon", "tokens": 8000},
                        {"date": "Tue", "tokens": 12000},
                        {"date": "Wed", "tokens": 10500},
                        {"date": "Thu", "tokens": 15000},
                        {"date": "Fri", "tokens": 7000},
                        {"date": "Sat", "tokens": 3000},
                        {"date": "Sun", "tokens": 5000}
                    ]
                },
                {
                    "id": "cost-breakdown",
                    "type": "pie",
                    "title": "Cost by Provider (%)",
                    "data": [
                        {"name": "Anthropic", "value": 40},
                        {"name": "Together.ai", "value": 35},
                        {"name": "OpenRouter", "value": 25}
                    ]
                }
            ]
        },
        "table_config": {
            "columns": [
                {"data": "name", "title": "Swarm"},
                {"data": "model", "title": "Model"},
                {"data": "success_rate", "title": "Success Rate"},
                {"data": "tokens_used", "title": "Tokens Used"}
            ],
            "data": [
                {"name": "Coder", "model": "sonnet", "success_rate": "92%", "tokens_used": "15,000"},
                {"name": "Planner", "model": "sonnet", "success_rate": "87%", "tokens_used": "8,000"},
                {"name": "Scout", "model": "haiku", "success_rate": "94%", "tokens_used": "3,000"},
                {"name": "Skeptic", "model": "sonnet", "success_rate": "89%", "tokens_used": "12,000"}
            ]
        },
        "diagram_mermaid": """graph LR
    Input["User Input"]
    Dispatch["Dispatch<br/>Router"]

    Coder["🔨 Coder<br/>sonnet"]
    Planner["📋 Planner<br/>sonnet"]
    Scout["🔍 Scout<br/>haiku"]
    Skeptic["⚖️ Skeptic<br/>sonnet"]

    Verify["Verification"]
    Output["Output"]

    Input --> Dispatch
    Dispatch -->|code/refactor| Coder
    Dispatch -->|plan/risk| Planner
    Dispatch -->|explore/research| Scout
    Dispatch -->|review/test| Skeptic

    Coder --> Verify
    Planner --> Verify
    Scout --> Verify
    Skeptic --> Verify

    Verify --> Output

    style Input fill:#e1f5ff,stroke:#01579b
    style Output fill:#c8e6c9,stroke:#1b5e20
    style Dispatch fill:#fff9c4,stroke:#f57f17""",
        "instructions": [
            {
                "step": "1",
                "title": "Select a swarm in the chat",
                "description": "Type 'swarm: coder' to run code tasks"
            },
            {
                "step": "2",
                "title": "Edit swarm config",
                "file": "data/default/orchestration.yaml",
                "button": "Open in VSCode"
            },
            {
                "step": "3",
                "title": "View success metrics",
                "command": "stillwater swarms metrics"
            }
        ]
    },
    "cpu": {
        "title": "CPU Nodes",
        "chat_prompt": "Ask about algorithm performance, optimization ideas, and CPU utilization",
        "report_config": {
            "type": "multi-chart",
            "charts": [
                {
                    "id": "latency",
                    "type": "line",
                    "title": "Algorithm Latency (ms)",
                    "data": [
                        {"algo": "Search", "latency": 2.3},
                        {"algo": "Sort", "latency": 1.8},
                        {"algo": "Parse", "latency": 3.5},
                        {"algo": "Compress", "latency": 5.2}
                    ]
                },
                {
                    "id": "throughput",
                    "type": "column",
                    "title": "Throughput (req/sec)",
                    "data": [
                        {"algo": "Search", "throughput": 450},
                        {"algo": "Sort", "throughput": 380},
                        {"algo": "Parse", "throughput": 280},
                        {"algo": "Compress", "throughput": 190}
                    ]
                },
                {
                    "id": "resources",
                    "type": "gauge",
                    "title": "Memory Usage (%)",
                    "value": 62
                }
            ]
        },
        "table_config": {
            "columns": [
                {"data": "algorithm", "title": "Algorithm"},
                {"data": "complexity", "title": "Complexity"},
                {"data": "avg_time_ms", "title": "Avg Time (ms)"},
                {"data": "executions", "title": "Executions"}
            ],
            "data": [
                {"algorithm": "BinarySearch", "complexity": "O(log n)", "avg_time_ms": "2.3", "executions": "1,245"},
                {"algorithm": "QuickSort", "complexity": "O(n log n)", "avg_time_ms": "1.8", "executions": "892"},
                {"algorithm": "YAMLParse", "complexity": "O(n)", "avg_time_ms": "3.5", "executions": "2,156"},
                {"algorithm": "ZstdCompress", "complexity": "O(n)", "avg_time_ms": "5.2", "executions": "567"}
            ]
        },
        "diagram_mermaid": """graph TD
    Input["Input Data"]

    Algo1["BinarySearch<br/>O(log n)<br/>2.3ms"]
    Algo2["QuickSort<br/>O(n log n)<br/>1.8ms"]
    Algo3["YAMLParse<br/>O(n)<br/>3.5ms"]
    Algo4["ZstdCompress<br/>O(n)<br/>5.2ms"]

    Profile["Profiler"]
    Optimize["Optimizer"]
    Output["Output"]

    Input --> Algo1
    Input --> Algo2
    Input --> Algo3
    Input --> Algo4

    Algo1 --> Profile
    Algo2 --> Profile
    Algo3 --> Profile
    Algo4 --> Profile

    Profile --> Optimize
    Optimize --> Output

    style Input fill:#e1f5ff,stroke:#01579b
    style Output fill:#c8e6c9,stroke:#1b5e20""",
        "instructions": [
            {
                "step": "1",
                "title": "View CPU metrics",
                "description": "Check algorithm performance in the charts above"
            },
            {
                "step": "2",
                "title": "Edit algorithms",
                "file": "data/default/swarms/core/scout.md",
                "button": "Open in VSCode"
            },
            {
                "step": "3",
                "title": "Profile performance",
                "command": "stillwater profile --algo=search"
            }
        ]
    },
    "llm": {
        "title": "LLM Settings",
        "chat_prompt": "Ask to test a model, switch providers, configure tokens, and manage costs",
        "report_config": {
            "type": "multi-chart",
            "charts": [
                {
                    "id": "token-cost",
                    "type": "line",
                    "title": "Token Cost ($, cumulative)",
                    "data": [
                        {"date": "Feb 17", "cost": 5.2},
                        {"date": "Feb 18", "cost": 9.8},
                        {"date": "Feb 19", "cost": 14.3},
                        {"date": "Feb 20", "cost": 18.9},
                        {"date": "Feb 21", "cost": 23.1},
                        {"date": "Feb 22", "cost": 27.4},
                        {"date": "Feb 23", "cost": 31.7}
                    ]
                },
                {
                    "id": "model-comparison",
                    "type": "column",
                    "title": "Cost per Task by Model ($)",
                    "data": [
                        {"model": "haiku", "cost": 0.001},
                        {"model": "sonnet", "cost": 0.005},
                        {"model": "opus", "cost": 0.015}
                    ]
                },
                {
                    "id": "uptime",
                    "type": "gauge",
                    "title": "Provider Uptime (%)",
                    "value": 99.8
                }
            ]
        },
        "table_config": {
            "columns": [
                {"data": "model_name", "title": "Model"},
                {"data": "provider", "title": "Provider"},
                {"data": "token_cost", "title": "Cost per 1M tokens"},
                {"data": "status", "title": "Status"}
            ],
            "data": [
                {"model_name": "haiku", "provider": "Anthropic", "token_cost": "$0.80", "status": "Active"},
                {"model_name": "sonnet", "provider": "Anthropic", "token_cost": "$3.00", "status": "Active"},
                {"model_name": "opus", "provider": "Anthropic", "token_cost": "$15.00", "status": "Active"},
                {"model_name": "llama-70b", "provider": "Together.ai", "token_cost": "$0.59", "status": "Inactive"}
            ]
        },
        "diagram_mermaid": """graph TD
    Task["User Task"]
    Router["LLM Router"]

    Haiku["🥋 Haiku<br/>$0.80/1M<br/>Speed: Fast"]
    Sonnet["🎼 Sonnet<br/>$3.00/1M<br/>Speed: Medium"]
    Opus["🎭 Opus<br/>$15.00/1M<br/>Speed: Slow"]

    Verify["Verification"]
    Output["Output"]

    Task --> Router
    Router -->|scout/simple| Haiku
    Router -->|normal| Sonnet
    Router -->|complex| Opus

    Haiku --> Verify
    Sonnet --> Verify
    Opus --> Verify

    Verify --> Output

    style Haiku fill:#fff9c4,stroke:#f57f17
    style Sonnet fill:#ffe0b2,stroke:#e65100
    style Opus fill:#f3e5f5,stroke:#4a148c""",
        "instructions": [
            {
                "step": "1",
                "title": "Configure LLM settings",
                "file": "data/default/llm_config.yaml",
                "button": "Open in VSCode"
            },
            {
                "step": "2",
                "title": "Switch models",
                "command": "stillwater llm config --model=sonnet"
            },
            {
                "step": "3",
                "title": "View cost breakdown",
                "command": "stillwater llm metrics"
            }
        ]
    },
    "sync": {
        "title": "Solace AGI Sync",
        "chat_prompt": "Ask to sync data, check status, manage cloud backup, and configure Firestore",
        "report_config": {
            "type": "multi-chart",
            "charts": [
                {
                    "id": "sync-status",
                    "type": "gauge",
                    "title": "Sync Progress (%)",
                    "value": 87
                },
                {
                    "id": "data-volume",
                    "type": "area",
                    "title": "Data Synced (GB, cumulative)",
                    "data": [
                        {"date": "Feb 17", "gb": 0.5},
                        {"date": "Feb 18", "gb": 1.2},
                        {"date": "Feb 19", "gb": 2.1},
                        {"date": "Feb 20", "gb": 3.5},
                        {"date": "Feb 21", "gb": 5.8},
                        {"date": "Feb 22", "gb": 8.2},
                        {"date": "Feb 23", "gb": 11.5}
                    ]
                },
                {
                    "id": "firestore-health",
                    "type": "gauge",
                    "title": "Firestore Health (%)",
                    "value": 95
                }
            ]
        },
        "table_config": {
            "columns": [
                {"data": "timestamp", "title": "Timestamp"},
                {"data": "action", "title": "Action"},
                {"data": "status", "title": "Status"},
                {"data": "bytes", "title": "Bytes"}
            ],
            "data": [
                {"timestamp": "2026-02-23 14:32", "action": "push", "status": "Success", "bytes": "2.3 MB"},
                {"timestamp": "2026-02-23 14:12", "action": "pull", "status": "Success", "bytes": "1.8 MB"},
                {"timestamp": "2026-02-23 13:52", "action": "verify", "status": "Success", "bytes": "0.5 MB"},
                {"timestamp": "2026-02-23 13:32", "action": "push", "status": "Success", "bytes": "3.1 MB"}
            ]
        },
        "diagram_mermaid": """graph LR
    Local["📁 Local<br/>Stillwater Repo"]
    API["☁️ Solace API<br/>solaceagi.com"]
    Firestore["🔥 Firestore<br/>Cloud Storage"]

    Encrypt["🔒 Encrypt<br/>AES-256-GCM"]
    Sync["🔄 Sync<br/>Manager"]
    Verify["✓ Verify<br/>Hash Check"]

    Local -->|push| Encrypt
    Encrypt -->|POST| API
    API -->|store| Firestore

    Firestore -->|pull| API
    API -->|GET| Verify
    Verify -->|decrypt| Local

    style Local fill:#e1f5ff,stroke:#01579b
    style API fill:#fff9c4,stroke:#f57f17
    style Firestore fill:#f3e5f5,stroke:#4a148c""",
        "instructions": [
            {
                "step": "1",
                "title": "Enable Firestore sync",
                "file": "data/default/solace_agi_config.yaml",
                "button": "Open in VSCode"
            },
            {
                "step": "2",
                "title": "Start sync daemon",
                "command": "stillwater sync daemon --interval=5m"
            },
            {
                "step": "3",
                "title": "View sync status",
                "command": "stillwater sync status"
            }
        ]
    }
}

# ============================================================================
# ROUTES
# ============================================================================


@router.get("/pages", response_model=PagesListResponse)
async def list_pages():
    """List all available pages."""
    return PagesListResponse(pages=list(PAGE_DEFINITIONS.keys()))


@router.get("/page/{page_name}/data", response_model=PageDataResponse)
async def get_page_data(page_name: str):
    """Get full data for a specific page."""
    if page_name not in PAGE_DEFINITIONS:
        raise HTTPException(status_code=404, detail=f"Page '{page_name}' not found")

    page_def = PAGE_DEFINITIONS[page_name]
    return PageDataResponse(
        title=page_def["title"],
        chat_prompt=page_def["chat_prompt"],
        report_config=page_def["report_config"],
        table_config=page_def["table_config"],
        diagram_mermaid=page_def["diagram_mermaid"],
        instructions=page_def["instructions"]
    )


@router.get("/page/{page_name}/metrics", response_model=MetricsResponse)
async def get_page_metrics(page_name: str):
    """Get current metrics for a page."""
    if page_name not in PAGE_DEFINITIONS:
        raise HTTPException(status_code=404, detail=f"Page '{page_name}' not found")

    # Return current timestamp and sample metrics
    return MetricsResponse(
        metrics={
            "timestamp": datetime.now().isoformat(),
            "page": page_name,
            "sample_data": True
        }
    )


@router.post("/vscode/open", response_model=VSCodeResponse)
async def open_in_vscode(request: VSCodeRequest):
    """Open a file in VSCode."""
    try:
        # Map relative paths to absolute paths (from repo root)
        repo_root = Path(__file__).parent.parent.parent
        file_path = repo_root / request.file

        # Security check: ensure path is within repo
        if not str(file_path.resolve()).startswith(str(repo_root.resolve())):
            return VSCodeResponse(
                success=False,
                message=f"Access denied: path outside repo root"
            )

        # Try to open in VSCode
        try:
            subprocess.Popen(["code", str(file_path)])
            return VSCodeResponse(
                success=True,
                message=f"Opening {request.file} in VSCode"
            )
        except FileNotFoundError:
            # VSCode not in PATH, but don't fail
            logger.warning(f"VSCode not found in PATH. File path: {file_path}")
            return VSCodeResponse(
                success=True,
                message=f"File path prepared: {file_path} (VSCode not found - copy path manually)"
            )
    except Exception as e:
        logger.error(f"Error opening VSCode: {str(e)}")
        return VSCodeResponse(
            success=False,
            message=f"Error: {str(e)}"
        )
