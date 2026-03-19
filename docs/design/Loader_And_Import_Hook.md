# Loader And Import Hook

## Purpose

Explain how PyRolyze decides whether to transform a module and how transformed
artifacts are cached.

## Current implementation

The import path is built around:

- `src/pyrolyze/import_hook.py`
- `src/pyrolyze/importer.py`

The import hook is opt-in through environment variables. When enabled,
`PyRolyzeFinder` wraps eligible Python source modules with a loader that:

1. reads source from the delegated loader
2. checks `#@pyrolyze` in the first two lines
3. computes a cache fingerprint from:
   - source text
   - source mtime
   - Python magic number
   - active transformer fingerprint
4. compiles the source or loads a cached artifact
5. stores the artifact on `module.__pyrolyze_artifact__`
6. delegates normal module execution

The current import hook is artifact-oriented. It does not replace standard
module execution with transformed execution.

## Code map

- eligibility and cache helpers
  - `src/pyrolyze/importer.py`
- meta-path finder and wrapped loader
  - `src/pyrolyze/import_hook.py`
- compiler entry point used by the hook
  - `src/pyrolyze/compiler/facade.py`
- transformer fingerprint source
  - `src/pyrolyze/compiler/kernel_loader.py`

## Primary tests

- `tests/test_compiler_markers.py`
- `tests/test_import_hook_cache.py`
- `tests/test_importer_cache_fingerprint.py`

## Known limitations

- transformation is keyed only off the source marker, not richer project policy
- the import hook stores compile artifacts, not transformed execution results
- cache storage is simple and not wired into Python's `__pycache__`

## Future proposals

- richer eligibility filters
- direct transformed execution through the import path
- stronger cache persistence strategy aligned with Python cache conventions
