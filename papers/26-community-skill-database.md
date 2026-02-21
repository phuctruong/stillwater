# The Stillwater Community Database: Design Principles for a Distributed Skill Library

**Status:** Draft (open-source; claims typed by lane below)
**Last updated:** 2026-02-20
**Scope:** Design principles for a community-maintained skill library, including manifest identity, quality gating, never-worse versioning, canonical review agents, governance, and comparison to existing package registries.
**Auth:** 65537 (project tag; see `papers/03-verification-ladder.md`)

---

## Claim Hygiene

Every empirical claim in this paper is tagged with its epistemic lane:

- **[A]** Lane A — directly witnessed by executable artifact in this repo
- **[B]** Lane B — framework principle, derivable from stated axioms or established computer science
- **[C]** Lane C — heuristic or reasoned forecast; useful but not proven
- **[*]** Lane STAR — unknown or insufficient evidence; stated honestly

See `papers/01-lane-algebra.md` for the formal epistemic typing system.

---

## Abstract

**[B] Thesis:** A community skill database for AI behavior engineering requires: (1) machine-parseable manifests with sha256 identity, (2) binary quality scoring at submission, (3) versioned skills with never-worse doctrine, and (4) canonical swarm agent types for review.

Software package registries — npm, PyPI, crates.io — proved that community-maintained libraries create more value than any single organization can produce alone. They also proved the failure modes: unmaintained packages, security vulnerabilities, supply chain attacks, version incompatibilities.

A community skill database for AI behavior faces all the same challenges plus one additional: skills can degrade in behavior without changing their text, because the behavior depends on the model interpreting the skill as well as the skill itself. This creates a behavioral identity problem that sha256 content hashing alone does not solve.

This paper proposes four design principles that address the known failure modes of package registries while adding the behavioral identity constraints specific to skill libraries. We compare the design to npm, PyPI, and crates.io, identify where existing registry designs apply directly and where new mechanisms are required.

---

## 1. Introduction: Why Community Matters for Skill Libraries

### 1.1 The Single-Org Ceiling

**[B]** A skill library maintained by a single organization has a hard ceiling on domain coverage: it can only include skills that the organization's contributors understand well enough to gate rigorously. For general-purpose AI deployment, this ceiling is too low — the long tail of domain-specific expertise (legal, medical, financial, scientific, engineering) is too broad for any single organization to cover.

**[A]** This repo's skill library demonstrates the single-org ceiling: eight skills covering fundamental patterns (coding discipline, planning loops, context hygiene, safety, orchestration). The library is deep in its coverage of these fundamental patterns but thin on domain specialization.

**[C]** A mature community skill database could contain hundreds or thousands of domain-specific skills. A medical imaging analysis skill, a regulatory compliance checking skill, a scientific literature review skill — each encoding domain expertise that would take a single-org team months to develop and gate.

### 1.2 The Value Proposition

**[B]** Community maintenance creates value in three ways:

1. **Domain coverage:** the community's aggregate domain expertise exceeds any single organization's
2. **Verification diversity:** independent reviewers with different domain expertise find different failure modes
3. **Evolution speed:** a large community can detect skill rot and propose fixes faster than a small team

**[C]** The analogy to open-source software: Linux, Python, and npm are more valuable than any comparable proprietary offering not primarily because they are free, but because the community has contributed depth and breadth that no single organization could match. The same dynamic applies to skill libraries.

### 1.3 The Four Design Principles

This paper defines four design principles for a community skill database:

1. **SHA256 identity:** every skill is identified by its sha256 content hash, enabling precise behavioral pinning
2. **Quality gate at submission:** binary scorecard required before entry into the production tier
3. **Never-worse versioning:** version bumps cannot weaken prior guarantees; breaking changes require major versions
4. **Canonical review agents:** standardized swarm agents for review, enforcing consistent evaluation across contributors

---

## 2. Design Principle 1: SHA256 Identity and MANIFEST.json

### 2.1 The Identity Problem

**[B]** Package registries solve identity with version strings: `numpy==1.26.0` pins to a specific release. This works for code because code behavior is determined by the code itself. Skills have an additional behavioral identity dimension: the same skill text may produce different behavior on different model versions.

This creates two distinct identity problems:
- **Content identity:** is this the exact skill text the author submitted?
- **Behavioral identity:** does loading this skill on model X produce the same behavior as loading it on model Y?

**[B]** SHA256 solves content identity precisely. Behavioral identity requires a behavioral hash — a fingerprint of behavior on canonical test inputs — which is model-specific.

### 2.2 The MANIFEST.json Schema

**[B]** Every skill in the community database must be accompanied by a `MANIFEST.json` with the following required fields:

```json
{
  "schema_version": "1.0.0",
  "skill_id": "prime-coder",
  "skill_version": "2.0.2",
  "sha256": "abc123...",
  "author": "phuctruong",
  "created_at": "2026-02-20T00:00:00Z",
  "scorecard": {
    "fsm_present": true,
    "forbidden_states_defined": true,
    "verification_ladder_declared": true,
    "null_zero_handling": true,
    "output_contract": true,
    "total": 5
  },
  "rung_achieved": 65537,
  "evidence_bundle_sha256": "def456...",
  "behavioral_hashes": {
    "claude-sonnet-4-6": "ghi789...",
    "gpt-4o-2024-11-20": null
  },
  "env_snapshot_sha256": "jkl012...",
  "dependencies": [],
  "composability_notes": "Compatible with phuc-forecast v1.1.0+, prime-safety v1.0.0+",
  "domain_tags": ["coding", "verification", "safety"],
  "model_requirements": {
    "min_parameter_count_b": 7,
    "instruction_following_required": true
  }
}
```

**[A]** The sha256 field is computed over the normalized skill content (paths repo-relative, timestamps stripped, canonical JSON sort keys — the same normalization as `prime-coder.md`'s deterministic normal form). This ensures that two semantically identical skills with whitespace differences produce the same sha256.

### 2.3 Behavioral Identity via Behavioral Hashes

**[B]** The `behavioral_hashes` field is keyed by model version string and contains a hash computed by running the skill's canonical test suite on that model and hashing the normalized outputs. This is model-specific: `prime-coder` on `claude-sonnet-4-6` has a different behavioral hash than on `gpt-4o`.

**[B]** The behavioral hash enables precise behavioral pinning: a deployment can require not just a content version of a skill, but a specific behavioral hash on a specific model. If the behavioral hash drifts (same content, different behavior on a new model version), the deployment can detect the drift and require re-gating.

**[*]** Maintaining behavioral hashes across all model families is operationally expensive. The practical approach: the submitter provides at least one behavioral hash (their primary model); the community fills in additional model hashes through voluntary testing. Null entries indicate "not tested on this model."

---

## 3. Design Principle 2: Quality Gate at Submission

### 3.1 The Submission Pipeline

**[B]** A skill submitted to the community database enters a gated pipeline before it becomes available in the production tier:

```
SUBMISSION
    ↓
CONTENT CHECK (sha256 valid, MANIFEST.json parseable, skill text non-empty)
    ↓
SCORECARD (5-criteria binary check; must score 5/5 for production tier)
    ↓
EVIDENCE REVIEW (evidence bundle present, rung claim verified against bundle)
    ↓
SWARM REVIEW (canonical review agents run; findings must be addressed)
    ↓
PRODUCTION (available for loading by community deployments)
```

Skills failing at any stage are returned to the submitter with specific failure details. There is no "partial approval."

### 3.2 The Two Tiers

**[B]** The community database operates in two tiers:

**Experimental tier:** Skills that pass content check and scorecard but have not completed evidence review or swarm review. Available for loading but labeled `experimental`. Deployments must opt-in to experimental skills.

**Production tier:** Skills that have completed the full submission pipeline, including swarm review and rung verification. Available for loading without explicit opt-in. Subject to the never-worse versioning doctrine.

**[B]** This two-tier design addresses the bootstrap problem: new contributors can submit skills to the experimental tier immediately, get community feedback, and iterate toward the production tier. The production tier retains strict quality guarantees.

### 3.3 Rung Requirements Per Tier

**[B]** Required minimum rung by tier:

- Experimental: no minimum rung (but must declare a rung target)
- Production: rung 641 minimum; rung 65537 required for skills making promotion claims

**[A]** This mirrors the rung ladder defined in `papers/03-verification-ladder.md`: rung 641 is "local correctness" — sufficient for use in production but not for making claims about external benchmarks. Rung 65537 is "promotion-grade" — the standard for skills that make strong behavioral guarantees.

---

## 4. Design Principle 3: Never-Worse Versioning

### 4.1 The Never-Worse Doctrine

**[B]** The never-worse doctrine, as stated in `skills/prime-coder.md`:

> Hard gates and forbidden states are strictly additive over time. Any version of a skill must be at least as constrained as all prior versions. Removing a gate or weakening a forbidden state requires a major version bump and an explicit deprecation plan.

This is a stronger guarantee than semantic versioning alone. Semantic versioning (semver) allows breaking changes in major versions. The never-worse doctrine adds the constraint that even major versions cannot remove safety gates — they can only restructure them.

**[B]** The practical effect: users who depend on a skill's safety properties can trust that upgrading to a newer version will not silently remove those properties, even across major version boundaries. If a safety property must change, it requires a new skill with a different skill_id, not a major version of the existing skill.

### 4.2 Version Comparison Protocol

**[B]** To enforce never-worse versioning, the submission pipeline runs a version comparison protocol:

```
For each version bump:
1. Extract FORBIDDEN_STATES from old and new versions
2. Check: is every state in old FORBIDDEN_STATES also in new FORBIDDEN_STATES?
   If no: BLOCKED (never-worse violation)
3. Extract rung requirements from old and new versions
4. Check: is new rung_required >= old rung_required for each claim type?
   If no: BLOCKED (never-worse violation)
5. Extract output_contract required fields from old and new versions
6. Check: is every required field in old contract also required in new contract?
   If no: BLOCKED (never-worse violation)
```

**[B]** This protocol is automatable: it requires only the MANIFEST.json and the skill text. The community database runs it on every version submission before human review begins.

### 4.3 Deprecation Paths

**[C]** When a skill genuinely needs to weaken a constraint (e.g., a forbidden state turns out to be too aggressive for a legitimate use case), the correct deprecation path:

1. Create a new skill with a new skill_id (`prime-coder-relaxed`) with the weakened constraint
2. Mark the original skill as deprecated with a pointer to the new skill
3. The new skill starts fresh in the submission pipeline (scorecard, evidence review, swarm review)

This is deliberately expensive: weakening a constraint should be a high-friction operation that requires full re-review. The cost is the safety property.

---

## 5. Design Principle 4: Canonical Review Agents

### 5.1 Why Canonical Agents

**[B]** Without canonical review agents, swarm review is inconsistent: different submitters run different review approaches, producing incomparable results. A skill reviewed by an aggressive adversarial agent may have very different coverage than one reviewed by a gentle consistency-checker.

**[B]** Canonical review agents standardize the review process: the same set of agents, with the same personas and instructions, reviews every skill submission. This produces comparable coverage across submissions and makes the review process auditable.

### 5.2 The Canonical Agent Set

**[B]** Drawing on the analysis in `papers/25-persona-based-review-protocol.md`, the canonical review agent set for a production-tier skill submission:

| Agent | Persona | Primary check | Required output |
|---|---|---|---|
| Skeptic | Turing | Formal specification gaps, unenforceable constraints | List of falsifiers |
| Scout | Thompson | Evidence grounding, artifact presence | List of ungrounded claims |
| Judge | Lovelace | Structural consistency, ownership conflicts | Consistency verdict |
| Adversary | Dijkstra | Edge cases, boundary conditions, invariant violations | Edge case report |
| Economist | Shannon | Compression efficiency, redundancy | Efficiency notes |

**[B]** The Skeptic and Scout are mandatory for all production submissions. Judge and Adversary are required for skills that make composability or safety claims. Economist is optional but recommended for skills that make compression gain claims.

### 5.3 The swarms/ Directory

**[A]** The canonical agents are defined in the `swarms/` directory of this repo. Each agent definition specifies:

- Persona instruction (minimal, task-focused — see section 7.3 of paper 25)
- Required output format (structured, machine-parseable)
- Minimum coverage requirements (e.g., Skeptic must find at least 3 falsifiers or explicitly state "no falsifiers found")
- Pass/fail criterion for the agent's review

**[A]** This directory structure makes the review process portable: any community database instance can load the canonical agents from the `swarms/` directory and run standardized review without custom configuration.

---

## 6. Governance Model: Who Can Approve Skills

### 6.1 The Trust Problem in Decentralized Systems

**[B]** Decentralized package registries face a governance problem: who has the authority to approve a package, revoke approval, or remove a malicious package? npm's 2022 supply chain attack (where a maintainer published malicious code) and PyPI's ongoing challenges with typosquatting demonstrate that governance failures in package registries have real consequences.

**[B]** A community skill database faces the same problem, with an additional dimension: a malicious skill can subtly weaken safety constraints or introduce forbidden-state violations without obvious symptoms. Detecting this requires domain expertise, not just content scanning.

### 6.2 The Three-Layer Governance Model

**[B]** A practical governance model for a community skill database:

**Layer 1: Automated gates** (no human required)
- Content check (sha256, MANIFEST.json format)
- Scorecard (5-criteria binary check)
- Never-worse version comparison

**Layer 2: Canonical agent review** (automated but interpretable)
- Canonical swarm agents run and produce structured findings
- Findings are published alongside the skill submission
- Users can inspect agent findings before loading a skill

**Layer 3: Human core team approval** (required for production tier)
- A small core team reviews agent findings and makes final production approval
- Core team membership is itself governed (transparent nomination, term limits, public voting record)
- Core team can escalate to broader community review for contentious submissions

**[B]** Layer 1 and Layer 2 are fully automated and run within minutes of submission. Layer 3 is the human bottleneck and the primary scaling challenge. The core team's review is assisted by the canonical agent findings, which reduces the expert review burden to resolving ambiguous findings rather than conducting primary review.

### 6.3 Emergency Revocation

**[B]** Any production-tier skill must be revocable if a security or safety issue is discovered post-approval. The revocation mechanism:

1. Any contributor can file a revocation request with evidence of the issue
2. Core team reviews within 24 hours (emergency protocol)
3. If confirmed, the skill is moved to `revoked` status; all MANIFEST.json entries for dependents are updated
4. A public notice is published with the issue description and mitigation

**[B]** The revocation mechanism is intentionally expensive to invoke (requires evidence, core team review) but fast when invoked (24 hours). This prevents abuse while ensuring genuine issues are handled quickly.

---

## 7. Comparison to Package Registries

### 7.1 npm

**[B]** Similarities: decentralized contribution, version-based identity, strong network effects, community governance.

**[B]** Key differences:
- npm packages are code; skills are behavioral specifications. Code behavior is determined solely by the code; skill behavior also depends on the model interpreting the skill.
- npm has no quality gate at submission; anyone can publish any package. The community database requires a scorecard pass for production tier.
- npm version semantics allow breaking changes in major versions without additional constraint. Never-worse doctrine adds the constraint that safety properties cannot be weakened even across major versions.

### 7.2 PyPI

**[B]** Similarities: open submission, version pinning, dependency declaration, hash-based integrity (PyPI uses sha256 for wheel files).

**[B]** Key differences:
- PyPI uses sha256 for file integrity; the community database adds behavioral hashes for model-specific behavioral identity. These are different concepts that both matter.
- PyPI has no canonical review agents; code review (where it happens) is entirely community-driven with no standardized process.
- PyPI's governance model (PEPs, PSF) is well-established but centered on language evolution, not package quality. The community database governance is centered on behavioral quality gates.

### 7.3 crates.io

**[B]** Similarities: ownership model (clear package ownership, transfer mechanism), version immutability (published versions cannot be changed, only yanked), quality signals (download count, test badges).

**[B]** Key differences:
- crates.io enforces semver discipline; the community database adds never-worse discipline as a constraint on top of semver.
- crates.io's `cargo test` integration provides automatic testing; the community database's canonical agent review provides behavioral coverage that unit tests alone cannot provide.
- crates.io's supply chain security (via cargo-audit) checks for known vulnerabilities in dependencies; the community database's scout review checks for evidence-free claims — a skill-specific supply chain risk.

### 7.4 The Novel Requirements

**[B]** Three requirements are genuinely novel to skill libraries and not addressed by any existing package registry:

1. **Behavioral identity:** sha256 content hash does not capture behavioral identity; behavioral hashes per model version are required.
2. **Never-worse doctrine:** existing registries allow any change in major versions; skills require safety monotonicity even across major versions.
3. **Canonical behavioral review:** existing registries rely on code testing (automated) or human code review (unstructured). Canonical swarm agents provide structured behavioral review that is automated but interpretable.

---

## 8. Roadmap and Open Problems

### 8.1 Near-Term Roadmap

**[C]** Approximate sequencing for community database implementation:

**Phase 1 (0-3 months):** MANIFEST.json schema finalization; automated scorecard tool; sha256 computation tool; basic submission pipeline (content check + scorecard only)

**Phase 2 (3-6 months):** Canonical agent definitions in `swarms/`; automated agent review pipeline; experimental tier operational

**Phase 3 (6-12 months):** Never-worse version comparison protocol; core team formation; production tier operational with human review layer

**Phase 4 (12+ months):** Behavioral hash collection across model families; composability matrix; dependency resolution; search and browse interface

### 8.2 Open Problems

**[*]** Several open problems do not have clear solutions as of early 2026:

**Open problem 1: Behavioral hash collection at scale.** Generating behavioral hashes for each skill across all major model families requires running canonical test suites on each model. At scale, this is operationally expensive. The right economics for this (who pays? volunteers? model providers?) are unclear.

**Open problem 2: Composability verification.** Verifying that two skills compose correctly without conflicts requires running the composed system on test inputs. At scale with hundreds of skills, pairwise composability testing is O(N²). Efficient composability verification is an open research problem.

**Open problem 3: Governance scaling.** A small core team reviewing all production submissions does not scale to thousands of submissions per month. The right governance structure for a large community database (delegation, domain-specific review boards, reputation-weighted voting) is an open design question.

**Open problem 4: Zombie skill detection.** Skills that passed review at time T may degrade in behavior as models evolve, without any change to the skill text. Detecting zombie skills requires periodic re-gating — but who decides when re-gating is required, and who pays for it?

---

## 9. Conclusion

**[B]** A community skill database for AI behavior engineering is the natural evolution of the Software 5.0 skill library concept. The four design principles proposed here — sha256 identity, quality gate at submission, never-worse versioning, and canonical review agents — address the known failure modes of package registries while adding the behavioral identity constraints specific to skill libraries.

**[B]** The comparison to npm, PyPI, and crates.io shows that existing registry designs provide useful precedents for decentralized contribution, version pinning, and governance, but that skill libraries require three genuinely novel mechanisms: behavioral identity, never-worse doctrine, and canonical behavioral review.

**[A]** This repo's `skills/` directory is the seed library. The `swarms/` directory is the seed for canonical review agents. The `papers/00-index.md` is the seed for skill indexing. These structures, combined with the MANIFEST.json schema proposed here, form the foundation for a community database when the community is ready.

**[*]** Whether the community grows to a scale where a formal database is warranted, and what governance structure it adopts, are open questions. The design principles in this paper are intended to be correct at any scale — from a dozen skills to tens of thousands.

---

## References

- `papers/05-software-5.0.md` — Software 5.0 theoretical foundation
- `papers/23-software-5.0-extension-economy.md` — extension economy (why community matters)
- `papers/24-skill-scoring-theory.md` — binary scorecard (quality gate mechanism)
- `papers/25-persona-based-review-protocol.md` — persona-based review (canonical agent basis)
- `papers/03-verification-ladder.md` — 641 → 274177 → 65537 rung gates
- `skills/prime-coder.md` — never-worse doctrine (operational reference)
- `skills/phuc-swarms.md` — canonical agent orchestration
- npm Inc. (2022). npm Supply Chain Attack Postmortem. (External reference)
- Python Software Foundation. (2024). PyPI Security Model. (External reference)
- The Rust Foundation. (2024). crates.io Governance. (External reference)

---

**Auth: 65537** (project tag; see `papers/03-verification-ladder.md`)
**License:** Apache 2.0
**Citation:**
```bibtex
@software{stillwater2026_community_db,
  author = {Truong, Phuc Vinh},
  title = {The Stillwater Community Database: Design Principles for a Distributed Skill Library},
  year = {2026},
  url = {https://github.com/phuctruong/stillwater/papers/26-community-skill-database.md},
  note = {Auth: 65537}
}
```
