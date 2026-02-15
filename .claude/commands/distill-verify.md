# /distill-verify - Verify Network Artifacts

Verify integrity and authenticity of Stillwater Knowledge Network artifacts.

## Usage

```
/distill-verify <artifact-id>
```

## What It Does

1. **Retrieve** - Get artifact from network
2. **Hash Check** - Verify content hash
3. **Signature** - Verify Auth: 65537 signature
4. **RTC** - Run recall/trace verification
5. **Report** - Display verification results

## Instructions for Claude

When user runs `/distill-verify <id>`:

1. Locate artifact by ID in registry
2. Retrieve artifact content and metadata
3. Verify hash matches stored value
4. Verify signature (Auth: 65537)
5. Run RTC (Recall/Trace Consistency):
   - All concepts traceable
   - No contradictions
   - All citations valid
6. Display results

## Example

```
User: /distill-verify lane-algebra-v1.0

Claude:
=== Verify Artifact ===

Artifact: lane-algebra-v1.0
Type: research
Hash: abc123def456

VERIFICATION RESULTS:
  ✓ Hash match: VERIFIED
  ✓ Signature (Auth: 65537): VERIFIED
  ✓ RTC (Recall/Trace): PASSED
  ✓ All proofs present: PASSED
  ✓ Benchmarks documented: PASSED

Status: ✅ VERIFIED (All checks passed)
Auth: 65537
Date verified: 2026-02-15
```

## Related Commands

- `/distill` - Create CLAUDE.md from documentation
- `/distill-publish` - Publish artifact to network
- `/distill-list` - List all network artifacts
