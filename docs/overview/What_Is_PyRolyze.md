# What Is PyRolyze?

PyRolyze is a compile-time reactive Python package.

It lets authors write declarative Python functions marked with `@pyrolyse`,
then lowers those functions into runtime-aware component entry points. The
runtime tracks slot ownership, keyed loop identity, state/effect bindings,
invalidations, committed UI, and backend reconciliation.

In the current package, PyRolyze includes:

- a source API in `src/pyrolyze/api.py`
- a versioned AST compiler in `src/pyrolyze/compiler/`
- a context-graph runtime in `src/pyrolyze/runtime/`
- backend adapters for PySide6 and Tkinter
- source-backed golden tests and versioned Python test runs

What it is good for:

- building reactive UI code in Python without manually wiring update logic
- testing AST-lowered output directly
- debugging rerender behavior through committed UI and context-graph tools
- experimenting with backend adapters built on a shared reconciler model

What it does not try to be:

- a generic template engine
- a hidden magic runtime with no observable internals
- a framework that treats all Python versions as AST-equivalent

The compiler and runtime are explicit about their boundaries:

- source files opt in with `#@pyrolyze`
- components opt in with `@pyrolyse`
- slotted value helpers opt in with `@pyrolyze_slotted`
- AST kernels are versioned under `src/pyrolyze/compiler/kernels/`

Good starting points:

- [../user/Authoring_Overview.md](../user/Authoring_Overview.md)
- [System_Map.md](System_Map.md)
- [../design/Architecture.md](../design/Architecture.md)
