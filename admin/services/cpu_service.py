"""CPU Service — deterministic computation web service.

Port: 8792
Purpose: Hash computation, rung validation, exact arithmetic.
Never uses LLM. Never uses float for verification paths.
"""

from fastapi import FastAPI
from pydantic import BaseModel, Field
import hashlib
import hmac
from fractions import Fraction

SERVICE_ID = "cpu-service"
SERVICE_TYPE = "cpu"
VERSION = "0.1.0"
PORT = 8792

app = FastAPI(title="Stillwater CPU Service", version=VERSION)

# --- Models ---

class HashRequest(BaseModel):
    data: str
    algorithm: str = Field(default="sha256", pattern="^(sha256|sha512|md5)$")
    hmac_key: str | None = None

class HashResponse(BaseModel):
    hash: str
    algorithm: str
    input_length: int

class RungValidationRequest(BaseModel):
    claimed_rung: int
    evidence_artifacts: list[str] = Field(default_factory=list)
    has_tests: bool = False
    has_red_green: bool = False
    has_security_review: bool = False

class RungValidationResponse(BaseModel):
    valid: bool
    achieved_rung: int
    claimed_rung: int
    gaps: list[str] = Field(default_factory=list)

class MathRequest(BaseModel):
    operation: str = Field(..., pattern="^(add|subtract|multiply|divide|compare|modulo)$")
    operand_a: str  # String to preserve exact representation
    operand_b: str

class MathResponse(BaseModel):
    result: str
    exact: bool = True
    operation: str

# --- Endpoints ---

@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "version": VERSION,
    }

@app.get("/api/service-info")
async def service_info():
    return {
        "service_id": SERVICE_ID,
        "service_type": SERVICE_TYPE,
        "name": "CPU Service",
        "version": VERSION,
        "port": PORT,
    }

@app.post("/api/cpu/hash", response_model=HashResponse)
async def compute_hash(req: HashRequest):
    data_bytes = req.data.encode("utf-8")
    if req.hmac_key:
        h = hmac.new(
            req.hmac_key.encode("utf-8"),
            data_bytes,
            getattr(hashlib, req.algorithm),
        )
    else:
        h = hashlib.new(req.algorithm, data_bytes)
    return HashResponse(
        hash=h.hexdigest(),
        algorithm=req.algorithm,
        input_length=len(data_bytes),
    )

@app.post("/api/cpu/validate-rung", response_model=RungValidationResponse)
async def validate_rung(req: RungValidationRequest):
    gaps = []
    achieved = 0

    # Rung 641: basic (tests exist)
    if req.has_tests and len(req.evidence_artifacts) > 0:
        achieved = 641
    else:
        if not req.has_tests:
            gaps.append("No tests provided")
        if not req.evidence_artifacts:
            gaps.append("No evidence artifacts")

    # Rung 274177: irreversible (red-green gate)
    if achieved >= 641 and req.has_red_green:
        achieved = 274177
    elif achieved >= 641:
        gaps.append("No red-green gate evidence")

    # Rung 65537: production (security review)
    if achieved >= 274177 and req.has_security_review:
        achieved = 65537
    elif achieved >= 274177:
        gaps.append("No security review")

    # Rung difficulty ordering (not numeric): 641 < 274177 < 65537
    _rung_rank = {0: -1, 641: 0, 274177: 1, 65537: 2}
    valid = False
    if req.claimed_rung in (641, 274177, 65537):
        valid = _rung_rank.get(achieved, -1) >= _rung_rank.get(req.claimed_rung, -1)

    return RungValidationResponse(
        valid=valid,
        achieved_rung=achieved,
        claimed_rung=req.claimed_rung,
        gaps=gaps,
    )

@app.post("/api/cpu/math", response_model=MathResponse)
async def exact_math(req: MathRequest):
    """Exact arithmetic using Fraction. Never float."""
    try:
        a = Fraction(req.operand_a)
        b = Fraction(req.operand_b)
    except (ValueError, ZeroDivisionError) as e:
        return MathResponse(result=f"ERROR: {e}", exact=False, operation=req.operation)

    ops = {
        "add": lambda: a + b,
        "subtract": lambda: a - b,
        "multiply": lambda: a * b,
        "divide": lambda: a / b if b != 0 else "ERROR: division by zero",
        "compare": lambda: str(1 if a > b else (-1 if a < b else 0)),
        "modulo": lambda: a % b if b != 0 else "ERROR: modulo by zero",
    }

    result = ops[req.operation]()
    if isinstance(result, str) and result.startswith("ERROR"):
        return MathResponse(result=result, exact=False, operation=req.operation)
    return MathResponse(result=str(result), exact=True, operation=req.operation)
