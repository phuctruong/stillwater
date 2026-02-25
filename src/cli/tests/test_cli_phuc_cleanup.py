from __future__ import annotations

import json
from pathlib import Path

from stillwater.cli import main


def test_cleanup_scan_and_apply_empty_scope(capsys) -> None:
    rc_scan = main(["cleanup", "scan", "--scope", "artifacts/does-not-exist", "--json"])
    assert rc_scan == 0
    scan_payload = json.loads(capsys.readouterr().out)
    assert scan_payload["ok"] is True
    receipt = Path(scan_payload["receipt"])
    assert receipt.exists()

    rc_apply = main(["cleanup", "apply", "--scan-receipt", str(receipt), "--json"])
    assert rc_apply == 0
    apply_payload = json.loads(capsys.readouterr().out)
    assert apply_payload["ok"] is True
    assert apply_payload["scan_receipt"] == str(receipt)
