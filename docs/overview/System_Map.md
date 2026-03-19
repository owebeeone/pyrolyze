# System Map

This is the current package shape.

```mermaid
flowchart TD
    A["Author Source\n#@pyrolyze + @pyrolyse"] --> B["Compiler Facade\nsrc/pyrolyze/compiler/facade.py"]
    B --> C["Kernel Loader\nselect exact or fallback AST kernel"]
    C --> D["Versioned Kernel\nsrc/pyrolyze/compiler/kernels/v3_14/"]
    D --> E["Transformed Python / AST / Debug Artifacts"]
    E --> F["Runtime Context Graph\nsrc/pyrolyze/runtime/context.py"]
    F --> G["Committed UI\nUIElement tuples"]
    G --> H["Reconciler\nsrc/pyrolyze/runtime/ui_nodes.py"]
    H --> I["Backend Adapters\nPySide6 / Tkinter"]

    F --> J["App Context Store\nGeneration tracking, app-scoped values"]
    F --> K["Visitor Tools\nCommitted graph capture and diff"]
    B --> L["Golden Tests and Version Harness\nsrc/pyrolyze/tests/"]
    M["Import Hook\nsrc/pyrolyze/import_hook.py"] --> B
    M --> N["Artifact Cache\nsrc/pyrolyze/importer.py"]
```

## Main pieces

- Source API
  - `src/pyrolyze/api.py`
  - `src/pyrolyze/hooks.py`
- Compiler
  - `src/pyrolyze/compiler/`
- Runtime
  - `src/pyrolyze/runtime/`
  - `src/pyrolyze/visitor.py`
- Backends
  - `src/pyrolyze/pyrolyze_pyside6.py`
  - `src/pyrolyze/pyrolyze_tkinter.py`
- Examples
  - `examples/grid_app.py`
  - `examples/run_grid_app.py`
- Tests
  - `tests/`

## Read next

- [../design/Architecture.md](../design/Architecture.md)
- [../user/Authoring_Overview.md](../user/Authoring_Overview.md)
- [../contributor/Versioned_Test_Runs.md](../contributor/Versioned_Test_Runs.md)
