# Import Hook Bytecode Reuse

Status: implemented and verified locally. Not committed.

## Correction

`SourceLoader` already supports Python-managed transformed bytecode with
transformer-fingerprint-aware invalidation. The import hook nevertheless
resolved the compiler artifact eagerly in `exec_module`, before Python could
accept bytecode. The default in-memory artifact cache therefore could not avoid
transformation on a fresh process, even with valid bytecode present.

The loader now obtains code through `SourceLoader.get_code` first. A miss uses
`source_to_code` to transform, compile and cache as before. A hit executes valid
transformed bytecode without requesting a compiler artifact.

## Diagnostic Metadata

The operator approved lazy construction of `module.__pyrolyze_artifact__` on a
warm import. The attribute remains available: its first request constructs and
caches the artifact, and subsequent requests return the same object. It describes
the source captured during import, not later source edits. Modules compiled on
the cold path already have the artifact and retain eager access to it.

On the warm path the loader chains a module-level `__getattr__` for this attribute,
preserving the authored fallback for other names. Artifact data is absent from
the module dictionary until requested. Inspectors requiring compiler diagnostics
should explicitly access the attribute rather than assume its eager presence
in `vars(module)`. Diagnostic construction is serialized per imported module.

The optional persistent artifact cache remains available; enabling it is not
required for Python bytecode reuse. This change does not introduce another disk
cache, change generated widget packaging, or implement the lazy-loading plan.

## Initial Evidence

The fresh-loader regression reproduced two compiler calls for two imports with
independent in-memory caches and valid transformed bytecode. It now requires one
call and verifies the second import executes the transformed value.

Focused coverage also checks lazy diagnostic identity, authored attribute
fallbacks, reload of an existing module, captured-source diagnostics, source and
transformer invalidation, corrupt magic and truncated bytecode. The import-hook
group passed 24 checks with two existing bootstrap skips on the Python assembly
backend; all these checks also passed in the final default-backend full suite.

Final full regression: 1,200 passed, 20 existing skips, one pre-existing failure
in the separately modified `tests/test_pyside6_host_surface_fuzz.py` negative
control, which expects the repaired Qt ordering defect to remain detectable.
That unrelated file was not changed by this correction.

A fresh-process demo import with default settings took 12.9 seconds before the
correction, with three compiler calls despite existing bytecode. Afterward it
took 1.1 seconds with zero compiler calls. Three subsequent fresh-process probes
took 1.212, 1.168 and 1.206 seconds, all with zero compiler calls. These are small
unprofiled probe samples, not a controlled benchmark distribution or a cold-cache
improvement claim. Initial compilation and module execution costs remain.
