"""
store/packager.py — Skill packager for Stillwater Store submissions.

Bundles a skill.md + evidence directory into a submission payload with a
SHA-256 manifest for integrity verification.

Class: SkillPackager
  bundle_skill(skill_path, evidence_dir, author, rung_claimed) → dict
  verify_bundle(bundle) → bool
  package_skill(skill_path, evidence_dir=None) → dict
  validate_frontmatter(content) → dict
  compute_sha256_manifest(files_dict) → dict

Rung target: 641 (local correctness + tests passing)
Network: OFF — no HTTP calls; local file operations only.

Design decisions:
  - SHA-256 over {skill_name + skill_content + author + rung_claimed} provides
    tamper-evidence without requiring external dependencies.
  - Evidence directory must exist and contain plan.json + tests.json +
    behavior_hash.txt (the same three files required by RungValidator).
  - Invalid rung values fail-closed with ValueError (null != zero).
  - All file reads are UTF-8; non-UTF-8 content raises cleanly.
  - package_skill reads YAML-style frontmatter (--- delimited) if present.
  - validate_frontmatter: required fields are name and version (semver).
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# Valid rung values per stillwater verification ladder
VALID_RUNGS = frozenset({641, 274177, 65537})

# Required evidence filenames
REQUIRED_EVIDENCE_FILES = frozenset({"plan.json", "tests.json", "behavior_hash.txt"})

# Semver pattern: MAJOR.MINOR.PATCH (optionally with pre-release / build metadata)
_SEMVER_PATTERN = re.compile(
    r"^\d+\.\d+\.\d+(?:[-+].+)?$"
)


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
    # Spec-required interface: package_skill, validate_frontmatter, compute_sha256_manifest
    # ------------------------------------------------------------------

    def package_skill(
        self,
        skill_path: Path,
        evidence_dir: Optional[Path] = None,
    ) -> Dict[str, Any]:
        """
        Create a submission payload dict from a skill .md file.

        Reads the skill file, extracts frontmatter (name, version, rung, description,
        scopes), optionally validates and includes evidence, computes a SHA-256 manifest
        of all included files, and returns the payload.

        Args:
            skill_path:   Path to skill .md file.
            evidence_dir: Optional path to evidence directory. If provided, validates
                          the bundle and includes evidence files in the payload.

        Returns:
            dict with keys:
              skill_content, frontmatter, evidence (or None), sha256_manifest,
              packaged_at (ISO8601 UTC string)

        Raises:
            FileNotFoundError: skill_path does not exist.
            ValueError:        Frontmatter validation fails (missing name or version).
            ValueError:        evidence_dir provided but missing required evidence files.
        """
        skill_path = Path(skill_path)
        if not skill_path.exists():
            raise FileNotFoundError(f"Skill file not found: {skill_path}")

        skill_content = skill_path.read_text(encoding="utf-8")

        # Extract and validate frontmatter
        fm_result = self.validate_frontmatter(skill_content)
        if not fm_result.get("valid"):
            raise ValueError(
                f"Frontmatter validation failed: {fm_result.get('errors', [])}"
            )
        frontmatter = fm_result.get("fields", {})

        # Build files dict starting with skill content
        files_dict: Dict[str, str] = {skill_path.name: skill_content}

        # Include evidence if provided
        evidence: Optional[Dict[str, str]] = None
        if evidence_dir is not None:
            evidence_dir = Path(evidence_dir)
            if not evidence_dir.exists() or not evidence_dir.is_dir():
                raise FileNotFoundError(f"Evidence directory not found: {evidence_dir}")
            missing = REQUIRED_EVIDENCE_FILES - {f.name for f in evidence_dir.iterdir()}
            if missing:
                raise ValueError(
                    f"Evidence directory is missing required files: {sorted(missing)}. "
                    f"Required: {sorted(REQUIRED_EVIDENCE_FILES)}"
                )
            evidence = {}
            for fname in REQUIRED_EVIDENCE_FILES:
                content = (evidence_dir / fname).read_text(encoding="utf-8")
                evidence[fname] = content
                files_dict[fname] = content

        sha256_manifest = self.compute_sha256_manifest(files_dict)

        return {
            "skill_content":  skill_content,
            "frontmatter":    frontmatter,
            "evidence":       evidence,
            "sha256_manifest": sha256_manifest,
            "packaged_at":    datetime.now(timezone.utc).isoformat(),
        }

    def validate_frontmatter(self, content: str) -> Dict[str, Any]:
        """
        Parse and validate YAML-style frontmatter from skill .md content.

        Frontmatter format:
          ---
          name: skill-name
          version: 1.0.0
          rung: 641
          description: Brief description
          scopes: [scope1, scope2]
          author: author-name
          depends_on: [dep1, dep2]
          ---

        Required fields: name, version (semver x.y.z format)
        Optional fields: rung, description, scopes, author, depends_on

        Args:
            content: Full text content of the skill .md file.

        Returns:
            dict with keys:
              valid:  bool — True if all required fields present and valid
              fields: dict of parsed frontmatter key-value pairs (empty if none found)
              errors: list of error strings (empty if valid)
        """
        errors: List[str] = []
        fields: Dict[str, Any] = {}

        # Extract frontmatter block (--- ... ---)
        fm_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
        if not fm_match:
            # No frontmatter found — missing required fields
            errors.append("No YAML frontmatter block found (expected --- delimited block at top of file)")
            return {"valid": False, "fields": fields, "errors": errors}

        fm_text = fm_match.group(1)

        # Parse simple key: value lines (no nested YAML; covers our use case)
        for line in fm_text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" not in line:
                continue
            key, _, value = line.partition(":")
            key = key.strip()
            value = value.strip()

            # Handle list values: [item1, item2] or inline comma-separated
            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1]
                items = [item.strip().strip("'\"") for item in inner.split(",") if item.strip()]
                fields[key] = items
            else:
                # Strip inline comments and quotes
                value = value.split("#")[0].strip().strip("'\"")
                # Coerce numeric values
                if value.isdigit():
                    fields[key] = int(value)
                else:
                    fields[key] = value

        # Validate required field: name
        if "name" not in fields or not fields["name"]:
            errors.append("Frontmatter missing required field: 'name'")

        # Validate required field: version (must be semver)
        if "version" not in fields or not fields["version"]:
            errors.append("Frontmatter missing required field: 'version'")
        elif not _SEMVER_PATTERN.match(str(fields.get("version", ""))):
            errors.append(
                f"Frontmatter 'version' must be semver format (x.y.z), "
                f"got: {fields.get('version')!r}"
            )

        # Validate optional rung if present (must be a valid rung)
        if "rung" in fields and fields["rung"] is not None:
            rung_val = fields["rung"]
            if isinstance(rung_val, str):
                try:
                    rung_val = int(rung_val)
                    fields["rung"] = rung_val
                except ValueError:
                    errors.append(f"Frontmatter 'rung' must be an integer, got: {fields['rung']!r}")
                    rung_val = None
            if rung_val is not None and rung_val not in VALID_RUNGS:
                errors.append(
                    f"Frontmatter 'rung' must be one of {sorted(VALID_RUNGS)}, "
                    f"got: {rung_val!r}"
                )

        return {
            "valid":  len(errors) == 0,
            "fields": fields,
            "errors": errors,
        }

    @staticmethod
    def compute_sha256_manifest(files_dict: Dict[str, str]) -> Dict[str, str]:
        """
        Compute a SHA-256 hash for each file in files_dict.

        Args:
            files_dict: {filename: file_content (str)} mapping.

        Returns:
            {filename: sha256_hex_string} for all files in files_dict.
        """
        manifest: Dict[str, str] = {}
        for filename, content in files_dict.items():
            if isinstance(content, bytes):
                data = content
            else:
                data = content.encode("utf-8")
            manifest[filename] = hashlib.sha256(data).hexdigest()
        return manifest

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
