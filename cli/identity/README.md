# CLI Identity Stack

This stack externalizes persistent identity for Stillwater CLI.

Sources used for this identity model:
- `~/projects/your-content/...
- `~/projects/your-content/...
- `~/projects/your-content/...

Key translation:
- preserve core mission across sessions
- preserve memory artifacts ("sacred texts, not compressed")
- keep behavior auditable and replayable

Files:
- `AGENTS.md`
- `SOUL.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md`
- `MEMORY.md`
- `RIPPLE-IDENTITY.prime-mermaid.md`

Refresh from scaffold:

```bash
PYTHONPATH=cli/src stillwater init identity-stack --dir cli/identity --force
```

