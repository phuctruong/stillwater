---
id: recipe.portal-traversal
version: 1.0.0
title: Portal Traversal (Safe Cross-Bubble Communication)
description: Safe, verifiable, and auditable communication between isolated knowledge bubbles (projects, modules, agents, or contexts). Identifies source and target bubbles, checks Bayesian overlap, establishes handshake, opens a narrow portal, compresses payload using prime words, validates meaning preservation, closes the portal, and verifies the REMIND-VERIFY-ACKNOWLEDGE triangle.
skill_pack:
  - prime-safety
  - phuc-portals
  - phuc-triangle-law
  - phuc-prime-compression
compression_gain_estimate: "Encodes 1–3 hours of manual cross-project context sharing (with all the attendant confusion about what was shared, when, and whether it was understood) into a 20-minute auditable portal lifecycle with meaning preservation proof"
steps:
  - step: 1
    action: "Identify source and target bubbles: read CNF capsule SOURCE_BUBBLE and TARGET_BUBBLE fields; locate boundary definition files for each bubble (NORTHSTAR.md, ROADMAP.md, or equivalent spec); emit scratch/portal_bubbles.json with bubble IDs, types, and boundary paths"
    artifact: "scratch/portal_bubbles.json — {source: {id, type, boundary_path}, target: {id, type, boundary_path}}"
    checkpoint: "Both source and target have non-null id and boundary_path; boundary files exist and are readable; type is one of: project|module|agent|context"
    rollback: "If either bubble undefined or boundary file not found, emit status=NEED_INFO listing which bubble spec is missing; do not proceed until both boundaries are defined"
  - step: 2
    action: "Compute Bayesian overlap: read both boundary definition files; identify shared concepts, shared vocabulary, and shared data types between source and target bubbles; compute overlap_score in range [0.0, 1.0] where 0 = no shared concepts and 1 = identical bubbles; emit scratch/portal_overlap.json"
    artifact: "scratch/portal_overlap.json — {source_concepts: [], target_concepts: [], shared_concepts: [], overlap_score: 0.0, overlap_threshold: 0.1, transfer_authorized: true|false}"
    checkpoint: "overlap_score is a float in [0.0, 1.0]; shared_concepts list is explicitly present (may be empty); transfer_authorized is set based on overlap_score >= overlap_threshold OR explicit authorization in capsule"
    rollback: "If overlap_score < 0.1 AND no explicit authorization in capsule, emit status=BLOCKED with reason 'Bayesian overlap below threshold; bubbles may be incompatible'; escalate to orchestrator"
  - step: 3
    action: "Establish handshake — REMIND vertex: send the REMIND signal to the target bubble by emitting a summary of what is about to be transferred (before transfer begins); record REMIND artifact; this establishes the pre-condition of the triangle"
    artifact: "scratch/portal_remind.json — {portal_id: <uuid>, remind_summary: '<one paragraph summary of transfer payload>', timestamp_logical: 0, vertex: 'REMIND'}"
    checkpoint: "portal_id is a non-null UUID; remind_summary is non-empty and describes the actual payload; vertex field is exactly 'REMIND'"
    rollback: "If REMIND cannot be established (target bubble unreachable), abort and emit BLOCKED; do not open portal without REMIND in place"
  - step: 4
    action: "Open portal: formally record portal as open in portal_manifest.json; assign portal_id (reuse from step 3); record source, target, overlap_score, opened timestamp; the portal is now live and the transfer budget clock starts"
    artifact: "scratch/portal_manifest.json — {portal_id, source_bubble, target_bubble, overlap_score, portal_opened: true, portal_closed: false, opened_at_logical: 1}"
    checkpoint: "portal_opened is true; portal_closed is false; portal_id matches step 3; overlap_score matches step 2"
    rollback: "If manifest write fails, abort; do not proceed with transfer if portal is not formally recorded as open"
  - step: 5
    action: "Compress payload using prime words: take the full transfer payload; apply phuc-prime-compression to replace verbose phrases with prime word equivalents; verify compression ratio and meaning preservation; emit scratch/portal_compressed_payload.json and scratch/portal_compression_audit.json"
    artifact: "scratch/portal_compressed_payload.json — compressed version of payload using prime words; scratch/portal_compression_audit.json — {original_tokens, compressed_tokens, compression_ratio, prime_words_used: [], meaning_preservation_test: {query, pre_response, post_response, match: true|false}}"
    checkpoint: "compression_ratio > 1.0 (compressed must be shorter than original); meaning_preservation_test.match is true; prime_words_used list is non-empty"
    rollback: "If meaning_preservation_test.match is false, re-compress with different prime word selection; if still fails after 2 attempts, transmit uncompressed with a warning logged; do not block on compression failure if meaning is preserved"
  - step: 6
    action: "Transfer compressed context: deliver the compressed payload to the target bubble; log the transfer in portal_manifest.json; update the handshake — VERIFY vertex: confirm that the target bubble received the payload and can parse it; emit scratch/portal_verify.json"
    artifact: "scratch/portal_verify.json — {portal_id, verify_summary: '<one sentence confirming receipt>', received_token_count: 0, parse_successful: true, timestamp_logical: 2, vertex: 'VERIFY'}"
    checkpoint: "parse_successful is true; received_token_count matches compressed_tokens from step 5; vertex field is exactly 'VERIFY'"
    rollback: "If parse fails, re-send uncompressed payload; if still fails, emit BLOCKED and close portal; log failure in portal_manifest.json"
  - step: 7
    action: "Validate meaning preservation end-to-end: run the same test query used in step 5 against the decompressed received payload; compare response to pre-compression baseline; confirm semantic equivalence; update portal_manifest with validation result"
    artifact: "scratch/portal_validation.json — {portal_id, test_query, pre_transfer_response, post_transfer_response, semantic_match: true|false, validation_method: '<description>'}"
    checkpoint: "semantic_match is true; validation_method is non-empty (not just 'looks the same'); test_query is non-trivial (not a yes/no question)"
    rollback: "If semantic_match is false, re-open transfer with corrected payload; maximum 2 retries; on third failure emit BLOCKED with full validation failure report"
  - step: 8
    action: "Close portal: update portal_manifest.json with portal_closed=true and closed timestamp; the portal lifetime is now complete; no further transfers permitted through this portal instance"
    artifact: "scratch/portal_manifest.json (updated) — {portal_closed: true, closed_at_logical: 3}"
    checkpoint: "portal_closed is true; portal_opened is still true (both should be true in a completed portal); closed_at_logical > opened_at_logical"
    rollback: "Portal close must always succeed; if manifest update fails, log manual closure required and treat as closed for audit purposes"
  - step: 9
    action: "Verify REMIND-VERIFY-ACKNOWLEDGE triangle: check that all three vertices are present (remind_summary, verify_summary, acknowledge step); emit final ACKNOWLEDGE signal confirming the transfer is complete and the triangle is closed; emit scratch/portal_acknowledge.json and final handshake_receipt.json"
    artifact: "scratch/portal_acknowledge.json — {portal_id, acknowledge_summary: '<one sentence confirming triangle complete>', timestamp_logical: 4, vertex: 'ACKNOWLEDGE'}; scratch/handshake_receipt.json — {portal_id, triangle_complete: true, all_vertices: ['REMIND','VERIFY','ACKNOWLEDGE'], meaning_preserved: true}"
    checkpoint: "triangle_complete is true; all_vertices list has exactly ['REMIND','VERIFY','ACKNOWLEDGE']; meaning_preserved matches semantic_match from step 7"
    rollback: "If any vertex is missing, the triangle is incomplete; emit BLOCKED with which vertex is missing; do not emit PASS with incomplete triangle"
forbidden_states:
  - PORTAL_WITHOUT_OVERLAP_CHECK: "Proceeding to step 3 without completing step 2 (overlap score computed and transfer_authorized confirmed)"
  - TRANSFER_WITHOUT_OPEN: "Transferring payload without formally recording portal as open in portal_manifest.json"
  - TRANSFER_WITHOUT_COMPRESSION: "Sending uncompressed raw payload across bubble boundary without attempting prime word compression first"
  - PORTAL_LEFT_OPEN: "Emitting final artifacts without portal_closed == true in portal_manifest.json"
  - TRIANGLE_INCOMPLETE: "Emitting handshake_receipt with triangle_complete == true when any vertex is missing"
  - MEANING_VALIDATION_SKIPPED: "Skipping step 7 because 'the transfer looked fine'; semantic validation is mandatory"
  - SECRET_ACROSS_BOUNDARY: "Transmitting credentials, PII, API keys, or raw secrets in transfer payload without explicit redaction and authorization"
  - NULL_ZERO_CONFUSION: "Treating overlap_score of 0.0 as undefined; zero overlap is a valid computed result (and a signal to abort)"
verification_checkpoint: "Run: python3 -c \"import json; m=json.load(open('scratch/portal_manifest.json')); assert m['portal_opened']==True; assert m['portal_closed']==True\" — must exit 0; Run: python3 -c \"import json; h=json.load(open('scratch/handshake_receipt.json')); assert h['triangle_complete']==True; assert h['meaning_preserved']==True; assert set(h['all_vertices'])=={'REMIND','VERIFY','ACKNOWLEDGE'}\" — must exit 0"
rung_target: 274177
---

# Recipe: Portal Traversal (Safe Cross-Bubble Communication)

## Purpose

Provide a deterministic, auditable protocol for transferring context between isolated knowledge bubbles. Bubbles exist to maintain separation of concerns — projects, modules, agents, and contexts should not bleed into each other without explicit, verified, and triangulated handshakes. This recipe encodes the full portal lifecycle with meaning preservation proof and triangle law verification.

## When to Use

- When sharing context between two separate projects (e.g., stillwater → solace-cli)
- When an agent in one domain needs context from another domain's boundary spec
- When a swarm needs to pass verified, compressed context to a sub-agent in a different module
- When testing whether two projects have sufficient conceptual overlap to collaborate

## Triangle Law (REMIND-VERIFY-ACKNOWLEDGE)

Every portal transfer must complete all three vertices of the triangle:

| Vertex | When | What |
|--------|------|------|
| REMIND | Before transfer | "Here is what I am about to send you" |
| VERIFY | After receipt | "I confirm I received and can parse this" |
| ACKNOWLEDGE | After validation | "I confirm the meaning was preserved" |

A transfer that skips any vertex is not a verified transfer — it is a hope.

## Overlap Score Interpretation

| Score | Meaning | Action |
|-------|---------|--------|
| 0.0 | No shared concepts | BLOCKED unless explicitly authorized |
| 0.1–0.3 | Low overlap | Proceed with caution; narrow portal |
| 0.3–0.7 | Medium overlap | Standard portal; full recipe |
| 0.7–1.0 | High overlap | Consider whether bubbles should be merged |
| 1.0 | Identical | Transfer unnecessary; bubbles are the same |

## Rung Target: 274177

This recipe targets rung 274177 (stability) because cross-bubble transfers involve:
- Multiple files being modified or read across project boundaries
- Meaning preservation that must be verified, not just assumed
- Triangle law completeness that must be auditable on replay

A rung 641 (local correctness) is insufficient for portal traversal — you need stability evidence that the transfer is reproducible and meaning-preserving.

## Output Artifacts

- `scratch/portal_bubbles.json` — bubble identification
- `scratch/portal_overlap.json` — Bayesian overlap computation
- `scratch/portal_remind.json` — REMIND vertex
- `scratch/portal_manifest.json` — portal lifecycle (open → closed)
- `scratch/portal_compressed_payload.json` — prime-compressed transfer payload
- `scratch/portal_compression_audit.json` — compression ratio and meaning test
- `scratch/portal_verify.json` — VERIFY vertex
- `scratch/portal_validation.json` — end-to-end meaning preservation
- `scratch/portal_acknowledge.json` — ACKNOWLEDGE vertex
- `scratch/handshake_receipt.json` — final triangle verification receipt
