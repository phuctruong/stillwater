from __future__ import annotations

import json
from pathlib import Path

from stillwater.cli import main


def test_init_agi_cli_creates_scaffold(tmp_path: Path) -> None:
    project_name = "demo-agent"
    rc = main(
        [
            "init",
            "agi-cli",
            project_name,
            "--dir",
            str(tmp_path),
            "--identity-stack",
        ]
    )
    assert rc == 0

    base = tmp_path / project_name
    assert (base / "README.md").exists()
    assert (base / ".stillwater" / "project.json").exists()
    assert (base / "ripples" / "system" / "default.prime-mermaid.md").exists()
    assert (base / "recipes" / "recipe.hello_world.prime-mermaid.md").exists()
    assert (base / "AGENTS.md").exists()
    assert (base / "SOUL.md").exists()

    meta = json.loads((base / ".stillwater" / "project.json").read_text(encoding="utf-8"))
    assert meta["name"] == project_name
    assert meta["template"] == "stillwater-agi-cli-v1"
    assert meta["identity_stack"] is True


def test_init_agi_cli_requires_force_for_existing_target(tmp_path: Path) -> None:
    project_name = "demo-force"
    rc1 = main(["init", "agi-cli", project_name, "--dir", str(tmp_path)])
    assert rc1 == 0

    rc2 = main(["init", "agi-cli", project_name, "--dir", str(tmp_path)])
    assert rc2 == 1

    rc3 = main(["init", "agi-cli", project_name, "--dir", str(tmp_path), "--force"])
    assert rc3 == 0
