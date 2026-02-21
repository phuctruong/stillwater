"""
store/packager.py — Skill packager for Stillwater Store submissions.

Bundles a skill.md + evidence directory into a submission payload with a
SHA-256 manifest for integrity verification.

Class: SkillPackager
  bundle_skill(skill_path, evidence_dir, author, rung_claimed) → dict
  verify_bundle(bundle) → bool

Rung target: 641 (local correctness + tests passing)
Network: OFF — no HTTP calls; local file operations only.

Design decisions:
  - SHA-256 over {skill_name + skill_content + author + rung_claimed} provides
    tamper-evidence without requiring external dependencies.
  - Evidence directory must exist and contain plan.json + tests.json +
    behavior_hash.txt (the same three files required by RungValidator).
  - Invalid rung values fail-closed with ValueError (null != zero).
  - All file reads are UTF-8; non-UTF-8 content raises cleanly.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional

# Valid rung values per stillwater verification ladder
VALID_RUNGS = frozenset({641, 274177, 65537})

# Required evidence filenames
REQUIRED_EVIDENCE_FILES = frozenset({"plan.json", "tests.json", "behavior_hash.txt"})


class SkillPackager:
    """
    Packages a skill file + evidence directory into a submission bundle dict.

    Usage:
        packager = SkillPackager()
        bundle = packager.bundle_skill(
            skill_path=Path("skills/prime-coder.md"),
            evidence_dir=Path("evidence/"),
            author="phuc",
            rung_claimed=641,
        )
        assert packager.verify_bundle(bundle)  # True if unmodified
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def bundle_skill(
        self,
        skill_path: Path,
        evidence_dir: Path,
        author: str,
        rung_claimed: int,
    ) -> Dict[str, Any]:
        """
        Bundle skill file + evidence into a submission payload dict.

        Args:
            skill_path:   Path to the skill .md file.
            evidence_dir: Directory containing plan.json, tests.json,
                          behavior_hash.txt.
            author:       Author / account name (display string).
            rung_claimed: Claimed rung (641 / 274177 / 65537).

        Returns:
            dict with keys:
              skill_name, skill_content, author, rung_claimed,
              manifest_sha256, evidence (dict of evidence file contents)

        Raises:
            ValueError:       rung_claimed is not a valid rung value.
            FileNotFoundError: skill_path or evidence_dir does not exist.
            ValueError:       evidence_dir is missing required files.
        """
        # Fail-closed: validate rung first (null != 0; unknown rung != 641)
        if rung_claimed not in VALID_RUNGS:
            raise ValueError(
                f"Invalid rung_claimed={rung_claimed!r}. "
                f"Must be one of {sorted(VALID_RUNGS)}."
            )

        skill_path = Path(skill_path)
        evidence_dir = Path(evidence_dir)

        # Validate paths exist
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_path}")
        if not evidence_dir.exists() or not evidence_dir.is_dir():
            raise FileNotFoundError(f"Evidence directory not found: {evidence_dir}")

        # Validate required evidence files
        missing = REQUIRED_EVIDENCE_FILES - {f.name for f in evidence_dir.iterdir()}
        if missing:
            raise ValueError(
                f"Evidence directory is missing required files: {sorted(missing)}. "
                f"Required: {sorted(REQUIRED_EVIDENCE_FILES)}"
            )

        # Read skill content
        skill_content = skill_path.read_text(encoding="utf-8")
        skill_name = skill_path.stem  # filename without extension

        # Read evidence files
        evidence: Dict[str, Any] = {}
        for fname in REQUIRED_EVIDENCE_FILES:
            evidence[fname] = (evidence_dir / fname).read_text(encoding="utf-8")

        # Compute SHA-256 manifest over stable canonical fields
        manifest_sha256 = self._compute_manifest_sha256(
            skill_name=skill_name,
            skill_content=skill_content,
            author=author,
            rung_claimed=rung_claimed,
        )

        return {
            "skill_name":      skill_name,
            "skill_content":   skill_content,
            "author":          author,
            "rung_claimed":    rung_claimed,
            "manifest_sha256": manifest_sha256,
            "evidence":        evidence,
        }

    def verify_bundle(self, bundle: Dict[str, Any]) -> bool:
        """
        Verify that a bundle dict has not been tampered with.

        Re-computes the SHA-256 manifest from the canonical fields and
        compares to the stored manifest_sha256.

        Returns True if the bundle is intact, False if tampered or malformed.
        """
        try:
            expected = self._compute_manifest_sha256(
                skill_name=bundle["skill_name"],
                skill_content=bundle["skill_content"],
                author=bundle["author"],
                rung_claimed=bundle["rung_claimed"],
            )
            return expected == bundle["manifest_sha256"]
        except (KeyError, TypeError, ValueError):
            return False

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_manifest_sha256(
        skill_name: str,
        skill_content: str,
        author: str,
        rung_claimed: int,
    ) -> str:
        """
        Compute SHA-256 over the canonical bundle payload.

        Canonical form: JSON with sorted keys → UTF-8 bytes → SHA-256 hex.
        This is deterministic across Python versions and platforms.
        """
        canonical = json.dumps(
            {
                "author":        author,
                "rung_claimed":  rung_claimed,
                "skill_content": skill_content,
                "skill_name":    skill_name,
            },
            sort_keys=True,
            ensure_ascii=True,
        )
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
