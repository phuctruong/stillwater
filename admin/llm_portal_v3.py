#!/usr/bin/env python3
"""
Stillwater LLM Portal v3.0 - Simplified Architecture
Auth: 65537 | Port: 8788 | Status: REFACTORED

Core Design:
1. Swarm Executor - Loads swarm metadata, injects skills, calls LLM
2. Recipe Executor - Runs recipes on CPU nodes (for prime recipes)
3. Web API - Simple endpoints for both swarm and recipe execution
4. CLI - Just orchestrator that hits the portal

Endpoints:
  POST /v1/swarm/execute      Execute swarm (swarm_type, prompt, model)
  POST /v1/recipe/execute     Execute recipe (recipe_name, task, context)
  GET  /v1/models             List available models
  GET  /health                Health check
"""

from __future__ import annotations

import sys
import json
import logging
import asyncio
import subprocess
import uuid
from pathlib import Path
from typing import Optional, Any
from datetime import datetime

# Logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)

# Add CLI to path
_CLI_SRC = Path(__file__).parent.parent / "cli" / "src"
if str(_CLI_SRC) not in sys.path:
    sys.path.insert(0, str(_CLI_SRC))

# Dependencies
try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
    import uvicorn
    import yaml
except ImportError as e:
    logger.error(f"Missing: {e}. Install: pip install 'fastapi[standard]' uvicorn pyyaml")
    sys.exit(1)

try:
    from stillwater.llm_client import LLMClient
except ImportError as e:
    logger.error(f"stillwater.llm_client not found: {e}")
    sys.exit(1)


# ============================================================
# Data Models
# ============================================================

class SwarmRequest(BaseModel):
    """Request to execute a swarm with given prompt."""
    swarm_type: str  # "coder", "mathematician", etc.
    prompt: str  # User prompt/task
    model: str  # "haiku", "sonnet", "opus"
    max_tokens: int = 2048
    temperature: float = 0.0


class SwarmResponse(BaseModel):
    """Response from swarm execution."""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    model: str
    tokens_used: Optional[int] = None
    timestamp: str


class RecipeRequest(BaseModel):
    """Request to execute a recipe on CPU nodes."""
    recipe_name: str  # "gmail", "github", etc.
    task: str  # Task description
    context: dict = {}  # Additional context


class RecipeResponse(BaseModel):
    """Response from recipe execution."""
    success: bool
    result: Optional[Any] = None
    error: Optional[str] = None
    recipe: str
    timestamp: str


class WebhookResult(BaseModel):
    """Webhook callback with result from background process."""
    request_id: str
    source: str  # "wrapper", "swarm", etc.
    status: str  # "success", "error", "timeout"
    response: Optional[dict] = None
    error: Optional[str] = None
    latency_ms: Optional[int] = None
    timestamp: str


class WebhookResultsResponse(BaseModel):
    """Response containing all webhook results."""
    total: int
    results: list[dict]
    timestamp: str


class WrapperRequest(BaseModel):
    """Request to execute Claude Code wrapper."""
    prompt: str  # Prompt to send to Claude
    model: str = "claude-haiku"  # Model to use
    timeout_seconds: int = 30  # Timeout for wrapper execution


class WrapperResponse(BaseModel):
    """Response from wrapper execution."""
    success: bool
    response: Optional[str] = None
    error: Optional[str] = None
    model: str
    latency_ms: Optional[int] = None
    timestamp: str


# ============================================================
# Swarm Executor
# ============================================================

class SwarmExecutor:
    """Executes swarms by loading metadata and injecting skills."""

    def __init__(self, swarms_dir: Path, skills_dir: Path):
        self.swarms_dir = swarms_dir
        self.skills_dir = skills_dir
        self.llm_client = LLMClient()

    def load_swarm_metadata(self, swarm_type: str) -> dict:
        """Load swarm metadata from swarms/{swarm_type}.md."""
        swarm_file = self.swarms_dir / f"{swarm_type}.md"
        if not swarm_file.exists():
            raise ValueError(f"Swarm not found: {swarm_file}")

        content = swarm_file.read_text(encoding="utf-8")

        # Extract YAML metadata
        lines = content.split("\n")
        end_idx = None
        for i in range(1, len(lines)):
            if lines[i].startswith("---"):
                end_idx = i
                break

        if end_idx is None:
            raise ValueError(f"Malformed swarm file: {swarm_file}")

        yaml_text = "\n".join(lines[1:end_idx])
        return yaml.safe_load(yaml_text) or {}

    def build_system_prompt(self, metadata: dict) -> str:
        """Build system prompt from skill pack in metadata."""
        skill_pack = metadata.get("skill_pack", [])
        system_parts = []

        for skill_name in skill_pack:
            skill_file = self.skills_dir / f"{skill_name}.md"

            if not skill_file.exists():
                # Try recursive search
                matches = list(self.skills_dir.rglob(f"{skill_name}.md"))
                if matches:
                    skill_file = matches[0]
                else:
                    logger.warning(f"Skill not found: {skill_name}")
                    continue

            content = skill_file.read_text(encoding="utf-8")

            # Extract QUICK LOAD if available
            if "<!-- QUICK LOAD" in content:
                start = content.find("<!-- QUICK LOAD")
                end = content.find("-->", start) + 3
                system_parts.append(f"## SKILL: {skill_name}\n{content[start:end]}")
            else:
                system_parts.append(f"## SKILL: {skill_name}\n{content[:1000]}")

        return "\n\n---\n\n".join(system_parts)

    def execute(
        self,
        swarm_type: str,
        prompt: str,
        model: str,
        max_tokens: int = 2048,
        temperature: float = 0.0,
    ) -> SwarmResponse:
        """Execute swarm: load skills, build system prompt, call LLM."""
        try:
            # Load metadata
            metadata = self.load_swarm_metadata(swarm_type)

            # Build system prompt with skills
            system_prompt = self.build_system_prompt(metadata)

            # Build messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ]

            # Call LLM
            result = self.llm_client.chat(
                messages,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=60.0,
            )

            return SwarmResponse(
                success=True,
                response=result.text,
                model=model,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Swarm execution failed: {e}")
            return SwarmResponse(
                success=False,
                error=str(e),
                model=model,
                timestamp=datetime.now().isoformat(),
            )


# ============================================================
# Recipe Executor (for CPU nodes)
# ============================================================

class RecipeExecutor:
    """Executes recipes on CPU nodes (for prime recipes integration)."""

    def __init__(self, recipes_dir: Path):
        self.recipes_dir = recipes_dir

    def execute(self, recipe_name: str, task: str, context: dict) -> RecipeResponse:
        """Execute recipe on CPU node."""
        try:
            recipe_file = self.recipes_dir / f"{recipe_name}.json"
            if not recipe_file.exists():
                raise ValueError(f"Recipe not found: {recipe_name}")

            # Load recipe
            recipe = json.loads(recipe_file.read_text())

            # TODO: Execute recipe with given task and context
            # This is a placeholder for actual CPU recipe execution
            logger.info(f"Executing recipe: {recipe_name}")

            return RecipeResponse(
                success=True,
                result={"status": "placeholder", "recipe": recipe_name},
                recipe=recipe_name,
                timestamp=datetime.now().isoformat(),
            )

        except Exception as e:
            logger.error(f"Recipe execution failed: {e}")
            return RecipeResponse(
                success=False,
                error=str(e),
                recipe=recipe_name,
                timestamp=datetime.now().isoformat(),
            )


# ============================================================
# FastAPI App
# ============================================================

app = FastAPI(
    title="Stillwater LLM Portal v3",
    description="Swarm executor + recipe executor",
    version="3.0.0",
)

# Initialize executors
_project_root = Path(__file__).parent.parent  # admin/llm_portal_v3.py -> admin -> stillwater
_swarms_dir = _project_root / "swarms"
_skills_dir = _project_root / "skills"
_recipes_dir = _project_root / "recipes"

swarm_executor = SwarmExecutor(_swarms_dir, _skills_dir)
recipe_executor = RecipeExecutor(_recipes_dir)

# Webhook results storage (in-memory, keyed by request_id)
_webhook_results = {}


# ============================================================
# Wrapper Executor
# ============================================================

class WrapperExecutor:
    """Executes Claude Code wrapper and waits for response."""

    def __init__(self, wrapper_url: str = "http://127.0.0.1:8080/api/generate"):
        self.wrapper_url = wrapper_url

    async def execute(
        self,
        prompt: str,
        model: str = "claude-haiku",
        timeout_seconds: int = 30,
    ) -> WrapperResponse:
        """Execute wrapper: call Claude synchronously, return response."""
        import time
        start_time = time.time()

        try:
            logger.info(f"Wrapper execute: {model} | prompt_len={len(prompt)}")

            # Call wrapper using curl (blocking but simple)
            cmd = [
                "curl",
                "-s",
                "-X", "POST",
                self.wrapper_url,
                "-H", "Content-Type: application/json",
                "-d", json.dumps({
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                }),
                "--max-time", str(timeout_seconds),
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_seconds + 5)
            elapsed = int((time.time() - start_time) * 1000)

            if result.returncode == 0:
                response = json.loads(result.stdout)
                return WrapperResponse(
                    success=True,
                    response=response.get("response", ""),
                    model=model,
                    latency_ms=elapsed,
                    timestamp=datetime.now().isoformat(),
                )
            else:
                return WrapperResponse(
                    success=False,
                    error=result.stderr or f"Exit code {result.returncode}",
                    model=model,
                    latency_ms=elapsed,
                    timestamp=datetime.now().isoformat(),
                )

        except subprocess.TimeoutExpired:
            elapsed = int((time.time() - start_time) * 1000)
            return WrapperResponse(
                success=False,
                error=f"Wrapper timeout after {timeout_seconds}s",
                model=model,
                latency_ms=elapsed,
                timestamp=datetime.now().isoformat(),
            )
        except Exception as e:
            elapsed = int((time.time() - start_time) * 1000)
            logger.error(f"Wrapper execution failed: {e}")
            return WrapperResponse(
                success=False,
                error=str(e),
                model=model,
                latency_ms=elapsed,
                timestamp=datetime.now().isoformat(),
            )


wrapper_executor = WrapperExecutor()


# ============================================================
# Health & Info Endpoints
# ============================================================

@app.get("/")
async def root() -> dict:
    """Root endpoint with API documentation."""
    return {
        "name": "Stillwater LLM Portal v3",
        "status": "operational",
        "version": "3.0.0",
        "endpoints": {
            "GET /": "This endpoint",
            "GET /health": "Health check",
            "GET /v1/models": "List available models",
            "POST /v1/swarm/execute": "Execute swarm with skill injection",
            "POST /v1/recipe/execute": "Execute recipe on CPU nodes",
        },
        "docs": {
            "openapi": "/openapi.json",
            "swagger": "/docs",
            "redoc": "/redoc",
        },
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/health")
async def health() -> dict:
    """Health check."""
    return {
        "status": "healthy",
        "portal": "v3.0.0",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/v1/models")
async def list_models() -> dict:
    """List available models."""
    return {
        "models": [
            {"id": "haiku", "name": "Claude Haiku 4.5"},
            {"id": "sonnet", "name": "Claude Sonnet 4.6"},
            {"id": "opus", "name": "Claude Opus 4.6"},
        ]
    }


# ============================================================
# Swarm Execution Endpoint
# ============================================================

@app.post("/v1/swarm/execute")
async def execute_swarm(request: SwarmRequest) -> SwarmResponse:
    """Execute swarm: load swarm metadata, inject skills, call LLM."""
    logger.info(
        f"Swarm execute: {request.swarm_type} | "
        f"model={request.model} | prompt_len={len(request.prompt)}"
    )

    response = swarm_executor.execute(
        swarm_type=request.swarm_type,
        prompt=request.prompt,
        model=request.model,
        max_tokens=request.max_tokens,
        temperature=request.temperature,
    )

    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)

    return response


# ============================================================
# Recipe Execution Endpoint (for CPU nodes)
# ============================================================

@app.post("/v1/recipe/execute")
async def execute_recipe(request: RecipeRequest) -> RecipeResponse:
    """Execute recipe on CPU node."""
    logger.info(f"Recipe execute: {request.recipe_name}")

    response = recipe_executor.execute(
        recipe_name=request.recipe_name,
        task=request.task,
        context=request.context,
    )

    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)

    return response


# ============================================================
# Wrapper Execution Endpoint
# ============================================================

@app.post("/v1/wrapper/execute")
async def execute_wrapper(request: WrapperRequest) -> WrapperResponse:
    """Execute Claude Code wrapper: call internally, wait for result, return."""
    logger.info(
        f"Wrapper execute: {request.model} | prompt_len={len(request.prompt)}"
    )

    response = await wrapper_executor.execute(
        prompt=request.prompt,
        model=request.model,
        timeout_seconds=request.timeout_seconds,
    )

    if not response.success:
        raise HTTPException(status_code=400, detail=response.error)

    return response


# ============================================================
# Webhook Endpoints (for background process callbacks)
# ============================================================

@app.post("/v1/webhook/result")
async def webhook_result(request: WebhookResult) -> dict:
    """Receive webhook callback from background process."""
    logger.info(f"Webhook result: {request.request_id} | {request.source} | {request.status}")

    # Store result
    _webhook_results[request.request_id] = request.dict()

    return {
        "success": True,
        "request_id": request.request_id,
        "message": "Result stored",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/v1/webhook/results")
async def get_webhook_results() -> WebhookResultsResponse:
    """Retrieve all webhook results."""
    results = list(_webhook_results.values())
    logger.info(f"Retrieving {len(results)} webhook results")

    return WebhookResultsResponse(
        total=len(results),
        results=results,
        timestamp=datetime.now().isoformat(),
    )


@app.get("/v1/webhook/results/{request_id}")
async def get_webhook_result(request_id: str) -> dict:
    """Retrieve specific webhook result by ID."""
    if request_id not in _webhook_results:
        raise HTTPException(status_code=404, detail=f"Result not found: {request_id}")

    return _webhook_results[request_id]


@app.post("/v1/webhook/clear")
async def clear_webhook_results() -> dict:
    """Clear all stored webhook results."""
    count = len(_webhook_results)
    _webhook_results.clear()
    logger.info(f"Cleared {count} webhook results")

    return {
        "success": True,
        "cleared_count": count,
        "timestamp": datetime.now().isoformat(),
    }


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Stillwater LLM Portal v3")
    parser.add_argument("--host", default="127.0.0.1", help="Host (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8788, help="Port (default: 8788)")
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload on file changes",
    )

    args = parser.parse_args()

    logger.info(f"Starting Stillwater LLM Portal v3")
    logger.info(f"  Host: {args.host}")
    logger.info(f"  Port: {args.port}")
    logger.info(f"  Swarms dir: {_swarms_dir}")
    logger.info(f"  Skills dir: {_skills_dir}")
    logger.info(f"  Recipes dir: {_recipes_dir}")

    uvicorn.run(
        "llm_portal_v3:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )
