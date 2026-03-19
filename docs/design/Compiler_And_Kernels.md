# Compiler And Kernels

## Purpose

Describe the compiler facade, versioned kernel model, and emitted debug
artifacts.

## Current implementation

The compiler entry point is the facade in `src/pyrolyze/compiler/facade.py`.
It provides:

- `analyze_source(...)`
- `lower_plan_to_ast(...)`
- `emit_transformed_source(...)`
- `build_debug_artifacts_for_source(...)`
- `load_transformed_namespace(...)`
- `compile_source(...)`
- `compile_source_with_env(...)`

The facade delegates parsing, detection, planning, rewrite, validation, and
execution to a versioned AST kernel selected by
`src/pyrolyze/compiler/kernel_loader.py`.

Current kernel policy:

- prefer exact `v<major>_<minor>` match
- otherwise fall back to the latest available kernel

Today only `src/pyrolyze/compiler/kernels/v3_14/` is checked in, so Python
`3.12`, `3.13`, `3.14`, and `3.15` all currently route through the same kernel.

The compiler also emits helper-source debug artifacts through
`src/pyrolyze/compiler/debug.py`.

## Code map

- public compiler exports
  - `src/pyrolyze/compiler/__init__.py`
- facade
  - `src/pyrolyze/compiler/facade.py`
- artifact models
  - `src/pyrolyze/compiler/artifacts.py`
- diagnostics
  - `src/pyrolyze/compiler/diagnostics.py`
- kernel protocol
  - `src/pyrolyze/compiler/kernel_api.py`
- kernel selection
  - `src/pyrolyze/compiler/kernel_loader.py`
- current kernel
  - `src/pyrolyze/compiler/kernels/v3_14/`
- debug artifact writing
  - `src/pyrolyze/compiler/debug.py`

## Primary tests

- `tests/test_ast_compiler_facade.py`
- `tests/test_ast_kernel_selection.py`
- `tests/test_ast_goldens.py`
- `tests/test_versioned_test_harness.py`
- `tests/test_ast_phase3_base_rewrite.py`
- `tests/test_ast_phase4_structural_rewrite.py`
- `tests/test_ast_phase5_component_call_rewrite.py`
- `tests/test_ast_phase5_state_effect_rewrite.py`
- `tests/test_ast_phase7_native_call_rewrite.py`

## Known limitations

- only one kernel is checked in
- some source-language features are still partial or evolving
- compile artifacts and debug artifacts are more mature than transformed import execution

## Future proposals

- additional kernels when AST behavior diverges
- richer warning/error reporting
- more structured source-map and provenance tooling
