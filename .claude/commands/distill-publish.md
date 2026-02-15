# /distill-publish - Publish to Stillwater Knowledge Network

Publish a CLAUDE.md artifact to the network.

## Usage

```
/distill-publish <path>
```

## What It Does

1. **Verify** - Check artifact structure
2. **Hash** - Compute SHA256 content hash
3. **Sign** - Sign artifact (Auth: 65537)
4. **Register** - Add to network registry
5. **Store** - Archive in content storage

## Instructions for Claude

When user runs `/distill-publish <path>`:

1. Verify the file exists and is valid
2. Compute SHA256 hash
3. Generate artifact metadata:
   - ID: Based on filename + version
   - Type: Detected from content
   - Hash: Content hash
   - Created: Timestamp
4. Register in local manifest
5. Show results:
   - Artifact ID
   - Hash
   - Type
   - Storage path
6. Verify published artifact

## Example

```
User: /distill-publish papers/lane-algebra.md

Claude:
=== Publish to Stillwater Network ===

Step 1: Verifying artifact...
  ✓ Valid research paper format
  ✓ Contains proofs and benchmarks

Step 2: Computing hash...
  SHA256: abc123def456...

Step 3: Generating metadata...
  ID: lane-algebra-v1.0
  Type: research
  Created: 2026-02-15T00:00:00Z

Step 4: Registering in network...

Step 5: Verifying publication...
  ✓ Hash verified
  ✓ Signature verified
  ✓ Network registration confirmed

PUBLISHED SUCCESSFULLY
  ID: lane-algebra-v1.0
  Hash: abc123def456
  Type: research
```

## Related Commands

- `/distill` - Create CLAUDE.md from documentation
- `/distill-verify` - Verify artifact in network
- `/distill-list` - List all network artifacts
