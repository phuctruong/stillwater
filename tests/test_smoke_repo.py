import json
from pathlib import Path


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
    root = Path(__file__).resolve().parents[1]
    notebooks = [
        root / "HOW-TO-CRUSH-OOLONG-BENCHMARK.ipynb",
        root / "HOW-TO-CRUSH-MATH-OLYMPIAD.ipynb",
        root / "PHUC-ORCHESTRATION-SECRET-SAUCE.ipynb",
        root / "HOW-TO-CRUSH-SWE-BENCHMARK.ipynb",
        root / "PHUC-SKILLS-SECRET-SAUCE.ipynb",
    ]

    for nb_path in notebooks:
        assert nb_path.exists(), f"Missing notebook: {nb_path}"
        text = nb_path.read_text(encoding="utf-8")
        # Heuristic: committed notebooks should not leak machine-specific absolute home paths.
        for prefix in ("/home/", "/Users/", "C:\\\\Users\\\\"):
            assert prefix not in text, f"Machine-specific path leak in: {nb_path} ({prefix})"

        nb = _load_notebook(nb_path)
        assert not _notebook_has_error_outputs(nb), f"Error output present in: {nb_path}"


def test_cli_imports() -> None:
    # Basic smoke test to ensure the package entrypoint imports.
    from stillwater.cli import main  # noqa: F401
    from stillwater.__main__ import main as module_main  # noqa: F401
