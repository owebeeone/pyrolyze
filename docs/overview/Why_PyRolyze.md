# Why PyRolyze?

PyRolyze exists to make reactive Python code feel direct without forcing authors
to hand-write the update machinery.

The package takes a source-level approach:

- authors write ordinary Python functions
- the compiler lowers those functions into explicit runtime operations
- the runtime reruns only the boundaries that became dirty
- the backend reconciler updates native widgets from committed UI state

That matters because UI code usually becomes complex in two places:

- state and effect lifecycles
- identity and update behavior in nested trees

PyRolyze makes those concerns visible and testable instead of hiding them in a
large opaque runtime.

Why the package uses AST transforms at all:

- source code stays readable and author-oriented
- generated helper source can be inspected directly
- compiler output can be regression-tested with goldens
- runtime behavior can be tested separately from author syntax

Why the package is strict about Python versions:

- AST structure changes across interpreter releases
- lowering correctness depends on node shape, fields, and unparse behavior
- versioned kernels are easier to reason about than scattered runtime checks

The practical promise is simple:

- write concise reactive Python
- keep the lowered behavior inspectable
- keep the runtime model explicit
- keep new Python-version support manageable

For the concrete system layout, see [System_Map.md](System_Map.md).
