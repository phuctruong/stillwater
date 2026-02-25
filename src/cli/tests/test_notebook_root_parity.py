from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from stillwater.cli import main


ROOT_NOTEBOOK_CASES: list[tuple[str, list[str]]] = [
    (
        "HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb",
        ["skills", "show", "prime-math"],
    ),
    (
        "HOW-TO-CRUSH-SWE-BENCHMARK.ipynb",
        ["skills", "show", "prime-coder"],
    ),
    (
        "PRIME-MERMAID-LANGUAGE-SECRET-SAUCE.ipynb",
        ["recipe", "lint", "--prime-mermaid-only"],
    ),
]


@pytest.mark.parametrize("notebook_name,base_cmd", ROOT_NOTEBOOK_CASES, ids=[c[0] for c in ROOT_NOTEBOOK_CASES])
def test_root_notebook_has_cli_parity(notebook_name: str, base_cmd: list[str]) -> None:
    root = Path(__file__).resolve().parents[3]
    nb_path = root / "notebooks" / notebook_name
    if not nb_path.exists():
        pytest.skip(f"Notebook not present in this workspace: {notebook_name}")

    cmd = list(base_cmd)
    if "--run-id" in cmd:
        idx = cmd.index("--run-id")
        cmd[idx + 1] = f"{cmd[idx + 1]}-{uuid.uuid4().hex[:8]}"

    rc = main(cmd)
    assert rc == 0, f"Parity command failed for {notebook_name}: {cmd}"


def test_books_supports_persistent_intelligence_docs() -> None:
    root = Path(__file__).resolve().parents[3]
    books_dir = root / "books"
    if not books_dir.exists():
        pytest.skip("books/ directory not present")

    rc_list = main(["books", "list", "--json"])
    assert rc_list == 0
    rc_show = main(["books", "show", "PERSISTENT-INTELLIGENCE"])
    assert rc_show == 0


def test_papers_supports_software5_docs() -> None:
    root = Path(__file__).resolve().parents[3]
    papers_dir = root / "papers"
    if not papers_dir.exists():
        pytest.skip("papers/ directory not present")

    rc_list = main(["papers", "list", "--json"])
    assert rc_list == 0
    rc_show = main(["papers", "show", "05-software-5.0"])
    assert rc_show == 0
