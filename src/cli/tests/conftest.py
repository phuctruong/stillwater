import os
import sys
from pathlib import Path

# Allow `import stillwater` without requiring an editable install in the test env.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
os.environ.setdefault("STILLWATER_HMAC_SECRET", "test-secret-for-ci")
