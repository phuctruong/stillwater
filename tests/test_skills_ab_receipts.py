from __future__ import annotations

import json

from stillwater.skills_ab import RunRecorder


def test_run_recorder_writes_receipts_and_manifest(tmp_path) -> None:
    rec = RunRecorder(tmp_path, "run_test")

    sys_meta = rec.record_system_prompt(variant="AB_guarded_coder", system_prompt="line1\r\nline2\n")
    assert sys_meta["path"].startswith("system_prompts/")
    assert "sha256" in sys_meta
    assert "sha256_raw" in sys_meta

    run_meta = rec.record_run(
        scenario="safety_injection_1",
        variant="AB_guarded_coder",
        user_prompt="user\r\nprompt",
        response="resp\r\nonse",
    )
    assert run_meta["user_prompt_path"].startswith("prompts/")
    assert run_meta["response_path"].startswith("responses/")
    assert "user_prompt_sha256_raw" in run_meta
    assert "response_sha256_raw" in run_meta

    mf = rec.write_manifest(git_sha="deadbee", backend="mock", model="mock-kungfu-v1")
    assert mf["path"] == "runs/run_test/manifest.json"
    assert "sha256" in mf

    manifest_path = tmp_path / "runs" / "run_test" / "manifest.json"
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert data["schema_version"] == "skills_ab_receipts_manifest_v1"
    assert data["run_id"] == "run_test"
    assert data["git_sha"] == "deadbee"
    assert data["backend"] == "mock"
    assert data["model"] == "mock-kungfu-v1"
    assert [f["path"] for f in data["files"]] == sorted(f["path"] for f in data["files"])
