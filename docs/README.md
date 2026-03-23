# PyRolyze Docs

This docs tree describes the `py-rolyze` package as it exists today.

It is organized by reader and task:

- [overview/What_Is_PyRolyze.md](overview/What_Is_PyRolyze.md)
  - quick orientation
  - what the package does now
  - where to start
- [overview/System_Map.md](overview/System_Map.md)
  - one-page system map
  - component relationships
- [design/Architecture.md](design/Architecture.md)
  - implementation-facing architecture
  - compiler, runtime, backends, tests
- [design/UI_Interface_Schema.md](design/UI_Interface_Schema.md)
  - `UiInterface` and `UiInterfaceEntry`
  - common, PySide6, tkinter, DearPyGui, and Hydo interface families
- [user/README.md](user/README.md)
  - authoring guide entry point
  - decorators, annotations, hooks, native UI, testing
- [contributor/README.md](contributor/README.md)
  - maintainer workflows
  - goldens, versioned test runs, AST kernels, tracing
- [reference/Glossary.md](reference/Glossary.md)
  - stable terms and quick lookup

Recommended reading order:

1. [overview/What_Is_PyRolyze.md](overview/What_Is_PyRolyze.md)
2. [overview/System_Map.md](overview/System_Map.md)
3. [user/Authoring_Overview.md](user/Authoring_Overview.md) for source authors
4. [user/Mount_And_Mount_Points.md](user/Mount_And_Mount_Points.md) for explicit backend attachment
5. [design/Architecture.md](design/Architecture.md) for maintainers
6. [contributor/Versioned_Test_Runs.md](contributor/Versioned_Test_Runs.md) for AST and version work

For a short note on how this tree is maintained, see
[DocumentationPlan.md](DocumentationPlan.md).
