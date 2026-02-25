from __future__ import annotations

import json
from pathlib import Path

from stillwater.cli import main


def test_kernel_config_supports_external_skill_and_book_dirs(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    skills_dir = tmp_path / "external_skills"
    books_dir = tmp_path / "external_books"
    papers_dir = tmp_path / "external_papers"
    recipes_dir = tmp_path / "external_recipes"
    skills_dir.mkdir(parents=True, exist_ok=True)
    books_dir.mkdir(parents=True, exist_ok=True)
    papers_dir.mkdir(parents=True, exist_ok=True)
    recipes_dir.mkdir(parents=True, exist_ok=True)

    (skills_dir / "custom-ext-skill.md").write_text("# custom ext skill\n", encoding="utf-8")
    (books_dir / "CUSTOM-BOOK.md").write_text("# custom book\n", encoding="utf-8")
    (papers_dir / "CUSTOM-PAPER.md").write_text("# custom paper\n", encoding="utf-8")
    (recipes_dir / "recipe.custom_ext.prime-mermaid.md").write_text(
        "# recipe custom ext\n\n```mermaid\nflowchart TD\n  A --> B\n```\n",
        encoding="utf-8",
    )
    swarm_settings = tmp_path / "swarm-settings.prime-mermaid.md"
    swarm_settings.write_text(
        "\n".join(
            [
                "# custom swarm",
                "SETTING phase_order = DREAM,FORECAST,DECIDE,ACT,VERIFY",
                "SETTING persona.scout = Test Scout",
                "SETTING skill_pack = prime-safety.md,phuc-context.md",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    cfg = {
        "skill_dirs": [str(skills_dir)],
        "books_dirs": [str(books_dir)],
        "papers_dirs": [str(papers_dir)],
        "recipe_dirs": [str(recipes_dir)],
        "swarm_settings_file": str(swarm_settings),
        "prompt_prefix": "cfg> ",
        "assistant_prefix": "cfg-assistant> ",
    }
    cfg_path = tmp_path / "kernel-config.json"
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    monkeypatch.setenv("STILLWATER_KERNEL_CONFIG", str(cfg_path))

    rc_skills = main(["skills", "list", "--source", "extension", "--json"])
    assert rc_skills == 0
    payload = json.loads(capsys.readouterr().out)
    names = {item["name"] for item in payload["skills"]}
    assert "custom-ext-skill.md" in names

    rc_books = main(["books", "list", "--json"])
    assert rc_books == 0
    books_payload = json.loads(capsys.readouterr().out)
    assert any("CUSTOM-BOOK.md" in p for p in books_payload["books"])

    rc_papers = main(["papers", "list", "--json"])
    assert rc_papers == 0
    papers_payload = json.loads(capsys.readouterr().out)
    assert any("CUSTOM-PAPER.md" in p for p in papers_payload["papers"])

    rc_twin_recipes = main(["twin", "/recipes", "--json"])
    assert rc_twin_recipes == 0
    twin_recipe_payload = json.loads(capsys.readouterr().out)
    assert twin_recipe_payload["ok"] is True
    assert twin_recipe_payload["source"] == "CPU"
    assert "recipe.custom_ext.prime-mermaid.md" in twin_recipe_payload["response"]
    assert "prime-safety.md" in twin_recipe_payload["route"]["swarm_skill_pack"]

    rc_kernel = main(["twin", "/kernel", "--json"])
    assert rc_kernel == 0
    kernel_payload = json.loads(capsys.readouterr().out)
    assert "external_skills" in kernel_payload["response"]
    assert "external_books" in kernel_payload["response"]
    assert "external_papers" in kernel_payload["response"]
    assert "external_recipes" in kernel_payload["response"]
    assert str(swarm_settings) in kernel_payload["response"]
    assert "Test Scout" in kernel_payload["response"]
