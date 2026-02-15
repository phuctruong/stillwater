# /distill-list - List Network Artifacts

List all artifacts in the Stillwater Knowledge Network.

## Usage

```
/distill-list
```

## What It Does

1. **Read Registry** - Parse manifest
2. **Format Output** - Display as table
3. **Show Count** - Total artifacts

## Instructions for Claude

When user runs `/distill-list`:

1. Check for network registry
2. Display artifacts in table format:
   - ID
   - Type (knowledge, recipe, etc.)
   - Hash (first 12 chars)
   - Created date

3. Show total count

## Example

```
User: /distill-list

Claude:
=== Stillwater Knowledge Artifacts ===

Total artifacts: 5

ID                              TYPE        HASH         CREATED
--------------------------------------------------------------
lane-algebra-v1.0              research    abc123def45  2026-02-15
counter-bypass-v1.0            research    def456abc12  2026-02-15
verification-ladder-v1.0       research    789xyz123ab  2026-02-15
oolong-100-percent-v1.0        benchmark   xyz123abc45  2026-02-15
haiku-swarm-guide-v1.0         guide       456def789xy  2026-02-15

Use 'distill-verify <id>' for details on a specific artifact.
```

## Related Commands

- `/distill` - Create CLAUDE.md from documentation
- `/distill-publish` - Publish artifact to network
- `/distill-verify` - Verify artifact in network
