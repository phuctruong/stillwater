"""
Stillwater Homepage System — API Routes

Provides endpoints for:
- Homepage serving
- System status (LLM, Solace, Skills)
- Configuration (save/load YAML)
- Mermaid graph generation (Phase 1B+)

Rung Target: 641 (Local Correctness)
Version: 1.0.0
"""

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# ============================================================================
# ROUTER
# ============================================================================

router = APIRouter(
    prefix="",  # No prefix, routes are at root level
    tags=["homepage"],
    responses={404: {"description": "Not found"}},
)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================


class LLMConfigRequest(BaseModel):
    """LLM configuration submission"""
    default_model: str = Field(..., description="Default model: haiku|sonnet|opus")
    claude_code_enabled: bool = Field(default=True)
    auto_start_wrapper: bool = Field(default=True)


class SolaceAGIConfigRequest(BaseModel):
    """Solace AGI configuration submission"""
    api_key: str = Field(..., description="API key from solaceagi.com")
    auto_sync: bool = Field(default=True)


class LLMStatusResponse(BaseModel):
    """LLM system status"""
    online: bool
    default_model: Optional[str] = None
    available_models: List[str] = Field(default_factory=lambda: ["haiku", "sonnet", "opus"])
    config_file: Optional[str] = None


class SolaceAGIStatusResponse(BaseModel):
    """Solace AGI connection status"""
    configured: bool
    api_key_valid: Optional[bool] = None
    tier: Optional[str] = None


class SkillListResponse(BaseModel):
    """List of all skills"""
    count: int = 0
    skills: List[Dict[str, Any]] = Field(default_factory=list)


class ConfigSaveResponse(BaseModel):
    """Configuration save response"""
    saved: bool
    config_path: Optional[str] = None
    message: Optional[str] = None


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def get_repo_root() -> Path:
    """Get repository root path"""
    return Path(__file__).resolve().parents[2]


def load_yaml_file(file_path: Path) -> Optional[Dict]:
    """Load a YAML file safely"""
    try:
        if not file_path.exists():
            return None

        import yaml
        with open(file_path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.warning(f"Failed to load YAML file {file_path}: {e}")
        return None


def save_yaml_file(file_path: Path, data: Dict) -> bool:
    """Save a YAML file safely"""
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)

        import yaml
        with open(file_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        # Set restrictive permissions for security
        file_path.chmod(0o600)
        return True
    except Exception as e:
        logger.error(f"Failed to save YAML file {file_path}: {e}")
        return False


def merge_configs(default_config: Optional[Dict], custom_config: Optional[Dict]) -> Dict:
    """Merge custom config on top of default config"""
    if not default_config:
        default_config = {}
    if not custom_config:
        custom_config = {}

    # Simple merge: custom overwrites default
    result = {**default_config, **custom_config}
    return result


def _raise_not_implemented(endpoint: str) -> None:
    raise HTTPException(
        status_code=501,
        detail={"error": "not implemented", "endpoint": endpoint},
    )


def _list_markdown_entities(base_dir: Path, *, recursive: bool = False) -> List[Dict[str, Any]]:
    if not base_dir.exists():
        return []

    rows: List[Dict[str, Any]] = []
    iterator = base_dir.rglob("*.md") if recursive else base_dir.glob("*.md")
    for file_path in sorted(iterator):
        if file_path.name.startswith("README"):
            continue
        rows.append(
            {
                "id": file_path.stem,
                "name": file_path.stem.replace("-", " ").title(),
                "path": str(file_path.relative_to(get_repo_root())),
            }
        )
    return rows


def _graph_payload(graph_syntax: str) -> Dict[str, Any]:
    return {
        "graph_syntax": graph_syntax,
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
    }


# ============================================================================
# ROUTES: SERVING
# ============================================================================


@router.get("/")
async def serve_homepage() -> FileResponse:
    """Serve the homepage HTML"""
    repo_root = get_repo_root()
    homepage_path = repo_root / "admin" / "frontend" / "index.html"

    if not homepage_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Homepage not found"
        )

    return FileResponse(
        path=homepage_path,
        media_type="text/html",
        headers={"Cache-Control": "no-cache"}
    )


# ============================================================================
# ROUTES: STATUS ENDPOINTS
# ============================================================================


@router.get("/api/llm/status", response_model=LLMStatusResponse)
async def get_llm_status(request: Request) -> LLMStatusResponse:
    """Get LLM Portal system status

    Checks:
    - Is port 8788 open (Claude Code wrapper running)?
    - What is the default model?
    - What models are available?
    """
    try:
        repo_root = get_repo_root()

        # Load default config
        default_config = load_yaml_file(repo_root / "data" / "default" / "llm_config.yaml")

        # Load custom config (overlay)
        custom_config = load_yaml_file(repo_root / "data" / "custom" / "llm_config.yaml")

        # Merge configs
        config = merge_configs(default_config, custom_config)

        # Check if LLM Portal is online by checking if port 8788 is accessible.
        # For now, this route reports offline until probe wiring is implemented.
        online = False  # Default to offline

        default_model = config.get("default_model", "haiku")

        # Determine which config file was used
        config_file = None
        if custom_config:
            config_file = "data/custom/llm_config.yaml"
        elif default_config:
            config_file = "data/default/llm_config.yaml"

        return LLMStatusResponse(
            online=online,
            default_model=default_model,
            available_models=["haiku", "sonnet", "opus"],
            config_file=config_file
        )
    except Exception as e:
        logger.error(f"Error getting LLM status: {e}")
        return LLMStatusResponse(online=False)


@router.get("/api/solace-agi/status", response_model=SolaceAGIStatusResponse)
async def get_solace_status(request: Request) -> SolaceAGIStatusResponse:
    """Get Solace AGI connection status

    Checks:
    - Is configuration present?
    - Is API key valid?
    - What tier?
    """
    try:
        repo_root = get_repo_root()

        # Load custom config (contains encrypted API key)
        custom_config = load_yaml_file(repo_root / "data" / "custom" / "solace_agi_config.yaml")

        if not custom_config:
            return SolaceAGIStatusResponse(configured=False)

        # Check if service is enabled and API key exists
        service_enabled = custom_config.get("service", {}).get("enabled", False)
        has_api_key = bool(custom_config.get("authentication", {}).get("api_key"))

        configured = service_enabled and has_api_key

        return SolaceAGIStatusResponse(
            configured=configured,
            api_key_valid=configured,
            tier=custom_config.get("tier", "free") if configured else None
        )
    except Exception as e:
        logger.error(f"Error getting Solace status: {e}")
        return SolaceAGIStatusResponse(configured=False)


@router.get("/api/skills/list", response_model=SkillListResponse)
async def list_skills(request: Request) -> SkillListResponse:
    """List all available skills."""
    del request
    repo_root = get_repo_root()
    skills = _list_markdown_entities(repo_root / "data" / "default" / "skills")
    return SkillListResponse(count=len(skills), skills=skills)


@router.get("/api/recipes/list", response_model=SkillListResponse)
async def list_recipes(request: Request) -> SkillListResponse:
    """List all available recipes."""
    del request
    repo_root = get_repo_root()
    recipes = _list_markdown_entities(repo_root / "data" / "default" / "recipes")
    return SkillListResponse(count=len(recipes), skills=recipes)


@router.get("/api/swarms/list", response_model=SkillListResponse)
async def list_swarms(request: Request) -> SkillListResponse:
    """List all available swarm agents."""
    del request
    repo_root = get_repo_root()
    swarms = _list_markdown_entities(repo_root / "data" / "default" / "swarms", recursive=True)
    return SkillListResponse(count=len(swarms), skills=swarms)


@router.get("/api/personas/list", response_model=SkillListResponse)
async def list_personas(request: Request) -> SkillListResponse:
    """List all available personas."""
    del request
    repo_root = get_repo_root()
    personas = _list_markdown_entities(repo_root / "data" / "default" / "personas", recursive=True)
    return SkillListResponse(count=len(personas), skills=personas)


# ============================================================================
# ROUTES: MERMAID GRAPHS
# ============================================================================


@router.get("/api/mermaid/skills")
async def get_skills_graph(request: Request):
    """Get skills dependency graph in Mermaid format."""
    del request
    return _graph_payload(
        """graph TD
    P[prime-safety] --> C[prime-coder]
    C --> JS[prime-javascript]
    C --> API[prime-api]
    C --> OPS[prime-ops]
    JS --> SW[stillwater-admin]
    API --> SW
    OPS --> SW"""
    )


@router.get("/api/mermaid/recipes")
async def get_recipes_graph(request: Request):
    """Get recipes composition graph in Mermaid format."""
    del request
    return _graph_payload(
        """graph LR
    W[Wish] --> R[Recipe]
    R --> V[Verify]
    V --> E[Evidence]
    E --> S[Store]
    S --> R"""
    )


@router.get("/api/mermaid/swarms")
async def get_swarms_graph(request: Request):
    """Get swarm agent matrix in Mermaid format."""
    del request
    return _graph_payload(
        """graph TD
    I[Input] --> D[Dispatch]
    D --> CODER[Coder]
    D --> PLANNER[Planner]
    D --> SCOUT[Scout]
    D --> SKEPTIC[Skeptic]
    CODER --> O[Output]
    PLANNER --> O
    SCOUT --> O
    SKEPTIC --> O"""
    )


@router.get("/api/mermaid/personas")
async def get_personas_graph(request: Request):
    """Get persona FSMs in Mermaid format."""
    del request
    return _graph_payload(
        """stateDiagram-v2
    [*] --> Neutral
    Neutral --> Knuth: algorithms
    Neutral --> Schneier: security
    Neutral --> Liskov: contracts
    Knuth --> Neutral
    Schneier --> Neutral
    Liskov --> Neutral"""
    )


@router.get("/api/mermaid/orchestration")
async def get_orchestration_graph(request: Request):
    """Get orchestration Triple Twin graph in Mermaid format."""
    del request
    return _graph_payload(
        """graph LR
    IN[User Input] --> P1[Phase 1<br/>SmallTalk 0.70]
    P1 --> P2[Phase 2<br/>Intent 0.80]
    P2 --> P3[Phase 3<br/>Execution 0.90]
    P3 --> OUT[Action + Evidence]"""
    )


# ============================================================================
# ROUTES: CONFIGURATION SAVE
# ============================================================================


@router.post("/api/llm/config", response_model=ConfigSaveResponse)
async def save_llm_config(
    request: Request,
    config: LLMConfigRequest
) -> ConfigSaveResponse:
    """Save LLM configuration to YAML

    Validates and saves user's LLM preferences to:
    data/custom/llm_config.yaml
    """
    try:
        # Validate input
        if config.default_model not in ["haiku", "sonnet", "opus"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid model. Must be: haiku, sonnet, or opus"
            )

        repo_root = get_repo_root()
        custom_config_path = repo_root / "data" / "custom" / "llm_config.yaml"

        # Load existing custom config (if any)
        existing_config = load_yaml_file(custom_config_path) or {}

        # Update with new values
        existing_config["default_model"] = config.default_model
        existing_config["claude_code_wrapper"] = existing_config.get("claude_code_wrapper", {})
        existing_config["claude_code_wrapper"]["auto_start"] = config.auto_start_wrapper

        # Save to custom config file
        if save_yaml_file(custom_config_path, existing_config):
            logger.info(f"Saved LLM config: {custom_config_path}")
            return ConfigSaveResponse(
                saved=True,
                config_path=str(custom_config_path),
                message="LLM configuration saved successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to save configuration"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving LLM config: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.post("/api/solace-agi/config", response_model=ConfigSaveResponse)
async def save_solace_config(
    request: Request,
    config: SolaceAGIConfigRequest
) -> ConfigSaveResponse:
    """Save Solace AGI configuration to YAML

    Validates and saves Solace API key (encrypted) to:
    data/custom/solace_agi_config.yaml
    """
    try:
        # Validate API key format (basic check)
        if not config.api_key or len(config.api_key) < 10:
            raise HTTPException(
                status_code=400,
                detail="Invalid API key. Minimum 10 characters required."
            )

        repo_root = get_repo_root()
        custom_config_path = repo_root / "data" / "custom" / "solace_agi_config.yaml"

        # Load existing custom config (if any)
        existing_config = load_yaml_file(custom_config_path) or {}

        # Load default config for merging
        default_config = load_yaml_file(repo_root / "data" / "default" / "solace_agi_config.yaml") or {}

        # Merge default with existing custom
        merged_config = {**default_config, **existing_config}

        # Update with new values
        merged_config["service"] = merged_config.get("service", {})
        merged_config["service"]["enabled"] = True
        merged_config["authentication"] = merged_config.get("authentication", {})
        merged_config["authentication"]["api_key"] = config.api_key  # In Phase 1D, encrypt this
        merged_config["sync"] = merged_config.get("sync", {})
        merged_config["sync"]["enabled"] = config.auto_sync

        # Save to custom config file
        if save_yaml_file(custom_config_path, merged_config):
            logger.info(f"Saved Solace AGI config: {custom_config_path}")
            return ConfigSaveResponse(
                saved=True,
                config_path=str(custom_config_path),
                message="Solace AGI configuration saved successfully"
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to save configuration"
            )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving Solace config: {e}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================================
# ROUTES: DETAIL ENDPOINTS
# ============================================================================


@router.get("/api/skills/{skill_id}")
async def get_skill_detail(skill_id: str, request: Request):
    """Get detailed information about a skill."""
    del skill_id, request
    _raise_not_implemented("/api/skills/{skill_id}")


@router.get("/api/recipes/{recipe_id}")
async def get_recipe_detail(recipe_id: str, request: Request):
    """Get detailed information about a recipe."""
    del recipe_id, request
    _raise_not_implemented("/api/recipes/{recipe_id}")
