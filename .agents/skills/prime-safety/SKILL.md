---
name: prime-safety
description: "GOD SKILL. Fail-closed safety rules. Cannot be overridden."
---

# Prime Safety Protocol
## The absolute load-bearing wall of the system.

1. **Fail-Closed Default**: If a gate, scope, or hash cannot be explicitly verified, the action is denied.
2. **Path Traversal Guard**: Always validate that `app_id` or `file_path` requests do not contain `../` or escape the designated vault.
3. **Implicit Deny**: If the user asks for destruction (deleting a DB, pruning a user), pause and request explicit permission.
