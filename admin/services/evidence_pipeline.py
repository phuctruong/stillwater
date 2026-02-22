"""Evidence Pipeline Service — evidence capture and chain management.

Port: 8790
Purpose: Capture evidence bundles, maintain SHA-256 hash chain, validate ALCOA+ compliance.
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

SERVICE_ID = "evidence-pipeline"
SERVICE_TYPE = "evidence"
VERSION = "0.1.0"
PORT = 8790

app = FastAPI(title="Stillwater Evidence Pipeline", version=VERSION)

# Storage (overrideable for tests)
EVIDENCE_DIR = Path.home() / ".stillwater" / "evidence"
CHAIN_FILE = EVIDENCE_DIR / "chain.json"

# --- Models ---

class EvidenceCapture(BaseModel):
    service_id: str
    action: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    artifacts: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

class EvidenceBundle(BaseModel):
    bundle_id: str
    service_id: str
    action: str
    timestamp: str
    artifacts: dict[str, Any]
    metadata: dict[str, Any]
    content_hash: str
    prev_hash: str
    chain_position: int

class ALCOAValidation(BaseModel):
    attributable: bool = False   # Can trace to actor
    legible: bool = False        # Human-readable
    contemporaneous: bool = False  # Captured at time of action
    original: bool = False       # Source data, not copy
    accurate: bool = False       # Verified correct
    complete: bool = False       # No missing fields
    consistent: bool = False     # Internally consistent
    enduring: bool = False       # Stored durably
    available: bool = False      # Retrievable

class ALCOAResult(BaseModel):
    compliant: bool
    score: int  # 0-9 (count of True dimensions)
    dimensions: ALCOAValidation
    gaps: list[str]

# --- Chain Management ---

def _get_chain_file() -> Path:
    """Return the current CHAIN_FILE (allows test overrides via module-level reassignment)."""
    return CHAIN_FILE

def _load_chain() -> list[dict]:
    chain_file = _get_chain_file()
    if chain_file.exists():
        with open(chain_file) as f:
            return json.load(f)
    return []

def _save_chain(chain: list[dict]) -> None:
    chain_file = _get_chain_file()
    chain_file.parent.mkdir(parents=True, exist_ok=True)
    with open(chain_file, "w") as f:
        json.dump(chain, f, indent=2, default=str)

def _compute_hash(data: dict) -> str:
    canonical = json.dumps(data, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

# --- Endpoints ---

@app.get("/api/health")
async def health():
    chain = _load_chain()
    return {
        "status": "ok",
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "version": VERSION,
        "chain_length": len(chain),
    }

@app.get("/api/service-info")
async def service_info():
    return {
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "name": "Evidence Pipeline",
        "version": VERSION,
        "port": PORT,
    }

@app.post("/api/evidence/capture", response_model=EvidenceBundle)
async def capture_evidence(req: EvidenceCapture):
    chain = _load_chain()
    prev_hash = chain[-1]["content_hash"] if chain else "genesis"

    content = {
        "service_id": req.service_id,
        "action": req.action,
        "timestamp": req.timestamp,
        "artifacts": req.artifacts,
        "prev_hash": prev_hash,
    }
    content_hash = _compute_hash(content)

    bundle = EvidenceBundle(
        bundle_id=f"ev-{len(chain):06d}",
        service_id=req.service_id,
        action=req.action,
        timestamp=req.timestamp,
        artifacts=req.artifacts,
        metadata=req.metadata,
        content_hash=content_hash,
        prev_hash=prev_hash,
        chain_position=len(chain),
    )

    chain.append(bundle.model_dump())
    _save_chain(chain)
    return bundle

@app.get("/api/evidence/chain")
async def get_chain():
    chain = _load_chain()
    return {"ok": True, "chain_length": len(chain), "chain": chain}

@app.get("/api/evidence/bundles")
async def list_bundles(limit: int = 50, offset: int = 0):
    chain = _load_chain()
    return {
        "ok": True,
        "total": len(chain),
        "bundles": chain[offset : offset + limit],
    }

@app.get("/api/evidence/bundles/{bundle_id}")
async def get_bundle(bundle_id: str):
    chain = _load_chain()
    for entry in chain:
        if entry.get("bundle_id") == bundle_id:
            return {"ok": True, "bundle": entry}
    raise HTTPException(status_code=404, detail=f"Bundle {bundle_id} not found")

@app.post("/api/evidence/validate", response_model=ALCOAResult)
async def validate_alcoa(bundle: dict):
    """Validate an evidence bundle against ALCOA+ criteria."""
    gaps = []
    dims = ALCOAValidation()

    # Attributable: has service_id
    if bundle.get("service_id"):
        dims.attributable = True
    else:
        gaps.append("Missing service_id (not attributable)")

    # Legible: has artifacts that are dict/str (human-readable)
    artifacts = bundle.get("artifacts", {})
    if isinstance(artifacts, dict) and len(artifacts) > 0:
        dims.legible = True
    else:
        gaps.append("No artifacts (not legible)")

    # Contemporaneous: has timestamp
    ts = bundle.get("timestamp", "")
    if ts:
        dims.contemporaneous = True
    else:
        gaps.append("Missing timestamp (not contemporaneous)")

    # Original: has content_hash (proves this is the source)
    if bundle.get("content_hash"):
        dims.original = True
    else:
        gaps.append("Missing content_hash (not verifiably original)")

    # Accurate: has prev_hash (chain integrity)
    if bundle.get("prev_hash"):
        dims.accurate = True
    else:
        gaps.append("Missing prev_hash (chain integrity not verifiable)")

    # Complete: has all required fields
    required = {
        "bundle_id",
        "service_id",
        "action",
        "timestamp",
        "artifacts",
        "content_hash",
        "prev_hash",
    }
    missing = required - set(bundle.keys())
    if not missing:
        dims.complete = True
    else:
        gaps.append(f"Missing fields: {missing}")

    # Consistent: content_hash matches recomputed hash
    content = {
        "service_id": bundle.get("service_id"),
        "action": bundle.get("action"),
        "timestamp": bundle.get("timestamp"),
        "artifacts": bundle.get("artifacts"),
        "prev_hash": bundle.get("prev_hash"),
    }
    recomputed = _compute_hash(content)
    if recomputed == bundle.get("content_hash"):
        dims.consistent = True
    else:
        gaps.append("content_hash does not match recomputed hash (inconsistent)")

    # Enduring: chain_position exists (stored in chain)
    if "chain_position" in bundle:
        dims.enduring = True
    else:
        gaps.append("No chain_position (not in evidence chain)")

    # Available: bundle_id exists (retrievable)
    if bundle.get("bundle_id"):
        dims.available = True
    else:
        gaps.append("No bundle_id (not retrievable)")

    score = sum(
        [
            dims.attributable,
            dims.legible,
            dims.contemporaneous,
            dims.original,
            dims.accurate,
            dims.complete,
            dims.consistent,
            dims.enduring,
            dims.available,
        ]
    )

    return ALCOAResult(
        compliant=score >= 7,  # 7/9 minimum for compliance
        score=score,
        dimensions=dims,
        gaps=gaps,
    )
