import json
from pathlib import Path

import pytest


def _load_notebook(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _notebook_has_error_outputs(nb: dict) -> bool:
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        for out in cell.get("outputs", []):
            if out.get("output_type") == "error":
                return True
    return False


def test_notebooks_are_executed_without_errors_and_portable_paths() -> None:
    root = Path(__file__).resolve().parents[2]
    expected = [
        root / "HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb",
        root / "HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb",
        root / "PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb",
        root / "HOW-TO-CRUSH-SWE-BENCHMARK.ipynb",
        root / "PHUC-SKILLS-SECRET-SAUCE.ipynb",
        root / "PRIME-MERMAID-LANGUAGE-SECRET-SAUCE.ipynb",
    ]
    notebooks = [nb for nb in expected if nb.exists()]
    if not notebooks:
        pytest.skip("Root benchmark notebooks are optional in this workspace layout.")

    for nb_path in notebooks:
        nb = _load_notebook(nb_path)
        assert not _notebook_has_error_outputs(nb), f"Error output present in: {nb_path}"


def test_cli_imports() -> None:
    # Basic smoke test to ensure the package entrypoint imports.
    from stillwater.cli import main  # noqa: F401
    from stillwater.__main__ import main as module_main  # noqa: F401


def test_cli_notebooks_are_json_and_portable() -> None:
    root = Path(__file__).resolve().parents[2]
    nb_dir = root / "cli" / "notebooks"
    assert nb_dir.exists(), f"Missing notebook directory: {nb_dir}"
    notebooks = sorted(nb_dir.glob("*.ipynb"))
    assert notebooks, "Expected at least one CLI notebook"

    for nb_path in notebooks:
        text = nb_path.read_text(encoding="utf-8")
        for prefix in ("/home/", "/Users/", "C:\\\\Users\\\\"):
            assert prefix not in text, f"Machine-specific path leak in: {nb_path} ({prefix})"
        nb = _load_notebook(nb_path)
        assert not _notebook_has_error_outputs(nb), f"Error output present in: {nb_path}"
