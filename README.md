# PyRolyze

PyRolyze is the rebooted compiler/runtime package for compile-time reactive Python plus PySide6.

This repository starts by carrying forward only the reusable scaffold from the original prototype:

- import-hook shell
- compiler diagnostic types
- runtime hook-slot skeleton
- adapter and external-store skeleton

The core compiler/rendering path is being rebuilt around:

- `@pyrolyse` component markers
- `#@pyrolyze` module opt-in comments on line 1 or 2
- example-driven AST transform specifications
- generated `target/*.py` review artifacts in the examples repo

User-facing source-language documentation lives in:

- `/Users/owebeeone/limbo/py-rolyze-dev2/docs/user/PyRolyze_Authoring_Guide.md`

## Current Status

Implemented in this repo today:

- source marker detection for `#@pyrolyze`
- `@pyrolyse` component discovery
- initial tests for the rebooted opt-in rules

Not yet implemented:

- executable init/update lowering
- direct Qt sink generation
- structural block runtime
- full external-store leak/race proof

## Local Development

Install the package in editable mode:

```bash
uv pip install -e .
```

Run focused tests:

```bash
uv run --with pytest --with pytest-cov pytest tests/test_compiler_markers.py -q
```
