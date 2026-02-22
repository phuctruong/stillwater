"""Recipe Engine data models."""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Any

class NodeType(str, Enum):
    LLM = "llm"
    CPU = "cpu"
    BROWSER = "browser"
    HUMAN = "human"
    COMPOSITE = "composite"

class RecipeStep(BaseModel):
    step_id: str
    node_type: NodeType
    action: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    expected_output: str | None = None
    timeout_ms: int = 5000

class RecipeDefinition(BaseModel):
    recipe_id: str
    name: str
    version: str = "0.1.0"
    description: str = ""
    steps: list[RecipeStep] = Field(default_factory=list)
    preconditions: list[str] = Field(default_factory=list)
    postconditions: list[str] = Field(default_factory=list)
    required_scopes: list[str] = Field(default_factory=list)
    deterministic: bool = False  # If true, can be cached
    metadata: dict[str, Any] = Field(default_factory=dict)

class RecipeExecution(BaseModel):
    execution_id: str
    recipe_id: str
    status: str = "pending"  # pending, running, completed, failed
    started_at: str = ""
    completed_at: str = ""
    results: list[dict] = Field(default_factory=list)
    evidence_bundle_id: str | None = None

class PMTriplet(BaseModel):
    """Precondition-Method-Postcondition triplet for recipe verification."""
    triplet_id: str
    recipe_id: str
    precondition: str
    method: str
    postcondition: str
    selector_hash: str = ""  # SHA-256 of selector for cache key

class RecipeCache(BaseModel):
    """Cache entry for deterministic recipes."""
    cache_key: str  # SHA-256 of recipe_id + input parameters
    recipe_id: str
    result: dict[str, Any]
    cached_at: str
    hit_count: int = 0
