# Publishing to PyPI

## First-time setup
```bash
pip install build twine
```

## Build the package
```bash
python -m build
ls dist/
```

## Test on TestPyPI first
```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ stillwater-os
stillwater --version
```

## Publish to PyPI
```bash
twine upload dist/*
```

## After publishing
Verify: pip install stillwater-os
