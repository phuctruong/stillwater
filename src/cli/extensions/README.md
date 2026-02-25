# CLI Extensions

This folder is the default customization layer for the Stillwater kernel.

Conventions:
- place custom skills in `skills/`
- place Prime Mermaid recipes in `recipes/`
- place persona files in `personas/`
- place identity overrides in `identity/`
- optional startup banner in `splash.txt`

Use with default kernel behavior (no env var needed), or point to another project:

```bash
export STILLWATER_EXTENSION_ROOT=/path/to/your/extension
./src/cli/stillwater-cli.sh twin --interactive
```

