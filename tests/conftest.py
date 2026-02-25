from __future__ import annotations

import os
import sys
from pathlib import Path


os.environ.setdefault("STILLWATER_HMAC_SECRET", "test-secret-for-ci")

_REPO_ROOT = Path(__file__).resolve().parents[1]
for _p in (
    _REPO_ROOT,
    _REPO_ROOT / "src",
    _REPO_ROOT / "src" / "cli" / "src",
):
    _p_str = str(_p)
    if _p_str not in sys.path:
        sys.path.insert(0, _p_str)
