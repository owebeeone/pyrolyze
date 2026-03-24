# Testing PyRolyze Code

Use more than one test layer.

## Good test layers

- compiler/golden tests
  - verify transformed source
- runtime tests
  - verify slot ownership, invalidation, effect behavior
- backend tests
  - verify native widget reconciliation
- integrated source-backed tests
  - verify real `@pyrolyze` source through compile + runtime

## Useful places in this repo

- golden source and expected output
  - `tests/data/gold_src/`
  - `tests/data/v3_14/goldens/`
- runtime/context tests
  - `tests/test_context_graph_*`
- integrated graph tests
  - `tests/test_visitor_context_graph.py`
  - `tests/test_visitor_context_graph_integrated.py`
- example host tests
  - `tests/test_examples_grid_app.py`
- dynamic mount and mount-advert behavior
  - many scenarios use `pyrolyze.testing.generic_backend` to generate minimal
    `@pyrolyze` component APIs for tests; see
    [../contributor/Generic_Backend_Testing.md](../contributor/Generic_Backend_Testing.md)

## Versioned Python runs

For AST-sensitive work, use the versioned harness:

- `tests/versioned_test_harness.py`

For details, read [../contributor/Versioned_Test_Runs.md](../contributor/Versioned_Test_Runs.md).
