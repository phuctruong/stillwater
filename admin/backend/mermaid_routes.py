"""
Mermaid-Interactive Routes
Provides API endpoints for orchestration diagram and node details.
"""

from fastapi import FastAPI, HTTPException
from pathlib import Path
import yaml
import json
from typing import Dict, Any, Optional


def create_mermaid_routes(app: FastAPI, repo_root: Path):
    """Register Mermaid-related routes with the FastAPI app."""

    # Load orchestration config once at startup
    def load_orchestration_yaml() -> Dict[str, Any]:
        """Load orchestration.yaml from data/default/orchestration.yaml"""
        config_path = repo_root / "data" / "default" / "orchestration.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"orchestration.yaml not found at {config_path}")

        with open(config_path, 'r') as f:
            data = yaml.safe_load(f)
        return data

    @app.get("/api/orchestration/mermaid")
    async def get_orchestration_mermaid():
        """
        GET /api/orchestration/mermaid
        Returns Mermaid syntax for the Triple Twin orchestration diagram.

        Example response:
        {
            "mermaid": "graph LR\n    explorer[\"Explorer<br/>haiku\"]-->builder[\"Builder<br/>sonnet\"]-->arbiter[\"Arbiter<br/>sonnet\"]",
            "nodes": ["explorer", "builder", "arbiter"]
        }
        """
        try:
            config = load_orchestration_yaml()
            twins = config.get("orchestration", {}).get("twins", {})

            # Build Mermaid graph: explorer -> builder -> arbiter
            mermaid_lines = ["graph LR"]
            node_ids = []

            for twin_key in ["explorer", "builder", "arbiter"]:
                if twin_key in twins:
                    twin_data = twins[twin_key]
                    role = twin_data.get("role", twin_key)
                    model = twin_data.get("model", "unknown")

                    # Create node with role and model
                    node_label = f"{twin_key.capitalize()}<br/>{model}"
                    mermaid_lines.append(f'    {twin_key}["{node_label}"]')
                    node_ids.append(twin_key)

            # Add edges: explorer -> builder -> arbiter
            if len(node_ids) >= 2:
                mermaid_lines.append(f"    {node_ids[0]}-->{node_ids[1]}")
            if len(node_ids) >= 3:
                mermaid_lines.append(f"    {node_ids[1]}-->{node_ids[2]}")

            mermaid_syntax = "\n".join(mermaid_lines)

            return {
                "mermaid": mermaid_syntax,
                "nodes": node_ids,
                "status": "ok"
            }
        except Exception as e:
            raise HTTPException(500, f"Failed to generate Mermaid diagram: {str(e)}")

    @app.get("/api/orchestration/node/{node_id}")
    async def get_node_details(node_id: str):
        """
        GET /api/orchestration/node/{node_id}
        Returns detailed information about a specific orchestration node.

        Supported node_ids: explorer, builder, arbiter

        Example response:
        {
            "id": "explorer",
            "name": "Explorer",
            "role": "scout",
            "model": "haiku",
            "type": "CPU",
            "persona": "Ken Thompson",
            "responsibility": "Research, exploration, discovery, problem analysis",
            "description": "Scout agent using Haiku model",
            "strengths": ["pattern_recognition", "breadth_search", "web_research", "file_navigation"],
            "tools": ["web_search", "grep", "glob", "read_files"],
            "rung_target": 641,
            "config_path": "swarms/scout.md",
            "algorithm": "graph TD\n    A[Input] --> B[Research] --> C[Output]",
            "examples": [
                "Explore codebase for pattern XYZ",
                "Search web for recent news on topic",
                "List all files matching pattern"
            ],
            "status": "ok"
        }
        """
        try:
            config = load_orchestration_yaml()
            twins = config.get("orchestration", {}).get("twins", {})

            # Validate node_id
            if node_id not in twins:
                raise HTTPException(404, f"Node '{node_id}' not found in orchestration")

            twin_data = twins[node_id]

            # Determine node type based on role
            role = twin_data.get("role", "unknown")
            node_type = "CPU" if role == "scout" else "Swarm"

            # Get config file path (based on role)
            config_paths = {
                "scout": "swarms/scout.md",
                "coder": "swarms/coder.md",
                "skeptic": "swarms/skeptic.md"
            }
            config_path = config_paths.get(role, f"swarms/{role}.md")

            # Example algorithms (simple flowcharts for each node)
            algorithms = {
                "explorer": "graph TD\n    A[Query] --> B[Research]\n    B --> C[Pattern Match]\n    C --> D[Findings]",
                "builder": "graph TD\n    A[Spec] --> B[Design]\n    B --> C[Implement]\n    C --> D[Test]\n    D --> E[Code]",
                "arbiter": "graph TD\n    A[Review] --> B[Analyze]\n    B --> C[Verify]\n    C --> D[Decision]"
            }
            algorithm = algorithms.get(node_id, "")

            # Example commands for each node
            examples = {
                "explorer": [
                    "Explore codebase for authentication patterns",
                    "Research competitive landscape for feature X",
                    "Search web for best practices on OAuth3",
                    "List all test files in project"
                ],
                "builder": [
                    "Implement null-check validation",
                    "Fix race condition in event handler",
                    "Refactor API endpoint for clarity",
                    "Write integration tests for new feature"
                ],
                "arbiter": [
                    "Review code quality metrics",
                    "Verify edge case handling",
                    "Check security best practices",
                    "Validate test coverage"
                ]
            }
            example_list = examples.get(node_id, [])

            return {
                "id": node_id,
                "name": node_id.capitalize(),
                "role": twin_data.get("role", "unknown"),
                "model": twin_data.get("model", "unknown"),
                "type": node_type,
                "persona": twin_data.get("persona", ""),
                "responsibility": twin_data.get("responsibility", ""),
                "description": f"{node_id.capitalize()} agent using {twin_data.get('model', 'unknown')} model",
                "strengths": twin_data.get("strengths", []),
                "tools": twin_data.get("tools", []),
                "rung_target": twin_data.get("rung_target", 641),
                "config_path": config_path,
                "algorithm": algorithm,
                "examples": example_list,
                "status": "ok"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(500, f"Failed to retrieve node details: {str(e)}")
