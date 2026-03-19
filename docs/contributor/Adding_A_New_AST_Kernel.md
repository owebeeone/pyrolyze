# Adding A New AST Kernel

## Purpose

Provide the current workflow for introducing a new kernel such as `v3_15`.

## Current implementation

Kernels live under:

- `src/pyrolyze/compiler/kernels/`

The current kernel module surface is:

- `kernel.py`
- `eligibility.py`
- `detect.py`
- `plan.py`
- `rewrite.py`
- `validate.py`
- `emit.py`
- helper modules such as `builders.py`

## Procedure

1. Confirm the break is AST- or lowering-specific.
2. Create a new directory such as `src/pyrolyze/compiler/kernels/v3_15/`.
3. Preserve the same kernel surface as `v3_14`.
4. Copy only the pieces that truly diverge.
5. Keep shared logic in non-versioned compiler modules where possible.
6. Add a matching golden directory:
   - `tests/data/v3_15/goldens/`
7. Regenerate goldens with the matching interpreter.
8. Run the full suite for that interpreter.

## Code map

- kernel selection
  - `src/pyrolyze/compiler/kernel_loader.py`
- kernel protocol
  - `src/pyrolyze/compiler/kernel_api.py`
- current kernel template
  - `src/pyrolyze/compiler/kernels/v3_14/`

## Primary tests

- `tests/test_ast_kernel_selection.py`
- `tests/test_ast_goldens.py`
- `tests/test_versioned_test_harness.py`

## Known limitations

- the current package has only one kernel, so `v3_14` is still the practical starting template

## Future proposals

- factor out more reusable helpers if multiple kernels start to diverge in the same ways
