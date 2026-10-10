# Rendering Backend Discussion Report

Recorded: 2026-10-04.

This captures a design discussion, not an implementation plan or authorization
to change rendering. Lifecycle integration and the isolated Tk packing fix
remain separate workstreams. Concrete defects and evidence are tracked in the
[Rendering Backend Bug List](RenderingBackendBugList.md).

## Current Rendering Model

Pyrolyze supports Qt 6 through PySide6, Tkinter, and Dear PyGui. Two author-facing
paths coexist:

| Path | Role |
| --- | --- |
| Generic semantic UI | Common element kinds translated by handwritten toolkit adapters; less native specificity. |
| Toolkit-native UI | Native widget definitions and capabilities, using generated libraries and the shared mountable engine. |
| Unified native API | Common names over the native path, not a third renderer; authors can mix unified and native elements. |

The [unified factory](../src/pyrolyze/unified/factory.py) already selects a backend.
Its [existing design](UnifiedMountBasedNativeApi.md) prioritizes useful common
names and composition, not identical behavior on every toolkit.

## Performance Discussion

The user's assessment is that current backends demonstrate viability for useful,
moderate-sized applications, but do not feel as responsive as browser-based
applications. This is an assessment, not a new benchmark result.

Rust could eventually accelerate matching, diffing, or mutation planning while
Python keeps component execution and AST transformations. A useful boundary
would exchange batches of tree data and edits, not make a native call per small
Python operation. This remains a proposal, with no prototype or speedup measured.

Changing language does not remove unnecessary work. The review distinguished:

- Repeated native Tk child-list queries: a confirmed Pyrolyze helper defect,
  not a demonstrated Tk defect.
- Missing native edit deltas: small updates can cause complete child reattachment
  without recreating the child objects.
- Repeated list snapshots/scans in semantic reconciliation: source-confirmed
  quadratic bookkeeping, but not yet a measured application bottleneck.
- Toolkit layout/paint and visible-window costs: separate from Python planning.

Existing GRIP/Pyrolyze dirty tracking already supports selective execution;
the proposal was not to invent another change-propagation system. A possible
future improvement is carrying trustworthy existing change information further
into mounting, which can still traverse retained output. Its benefit is unmeasured.

Broader profiling, Rust reconciliation, and native Qt on-demand catalog loading
are deferred. The Qt visual-ordering regression remains gated on the agreed
lifecycle checkpoint. The bug list records the narrower investigations separately.

## Unified Native API Gaps

The desired direction is a practical common denominator backed by native nodes,
with explicit native escape hatches. It is not automatic translation of arbitrary
Qt applications, pixel-perfect parity, or another rendering engine.

The current [shared surface](../src/pyrolyze/unified/base.py) has 18 helpers.
The main gaps are:

1. **Structure:** no common window, row, column, grid, or panel surface.
   [Reference shells](../tests/unified/e2e/test_reference_shell_layout.py) still
   use different backend hosts and mount selectors.
2. **Interaction:** button events are `on_clicked` on Qt, `on_command` on Tk,
   and `on_press` on Dear PyGui. Adapters do not normalize them into one contract.
3. **Properties:** extra `**props` expose native options, not a portable set for
   enabled state, visibility, sizing, spacing, and alignment.
4. **Behavior:** Dear PyGui ignores numeric step and separator orientation;
   radio grouping differs; Tk's scroll-panel adapter emits only a canvas shell.
5. **Presentation:** shared theme/density/typography keys exist, but components
   must currently read and translate them; adapters do not apply them automatically.
6. **Verification:** current tests emphasize emitted shapes and initial mounting,
   not one unchanged application with consistent edit/click/update behavior.

One suspected correctness defect was added as bug-list item 8: the Dear PyGui
adapter drops an explicit empty text value, while the engine retains omitted
properties. Clearing a retained populated field therefore lacks an update request.
This is supported by source inspection, not yet a live-GUI reproduction.

A suggested future proof is one unchanged small form on all three backends:
layout, text entry, toggle, and button, covering events, clearing/repopulating
values, and child updates. Strengthen the existing layer before widening the
widget catalog. This proof has not been authorized for implementation.

## Browser Hosting And Python

VS Code uses Electron and Chromium, as described in
[Microsoft's documentation](https://code.visualstudio.com/docs/setup/network).
The installed Cursor and ChatGPT/Codex bundles inspected during this discussion
also contain Electron/browser machinery. That observation is build-specific,
not a claim about every platform or historical ChatGPT version.

Browser technology alone does not explain responsiveness. Scheduling expensive
work away from the UI thread and limiting updates also matter; see
[VS Code's architecture account](https://code.visualstudio.com/blogs/2022/11/28/vscode-sandbox).

Electron exposes native C++ implementations through V8/Node bindings, but is
not merely a thin synchronous FFI: its browser model includes separate processes.
It supplies no official Python application binding equivalent to PySide for Qt.
Python is not fundamentally excluded from hosting Chromium, however.

| Option | Integration Shape |
| --- | --- |
| Electron plus Python | Node launches a Python process; messages flow through pipes or sockets and a restricted renderer bridge. |
| pywebview | Python-first browser host with a built-in Python/JavaScript bridge; engine selection varies by platform. |
| PySide6 Qt WebEngine | Supported Python bindings to Qt's Chromium-based browser host, without requiring Electron or Node. |

Sources: [Electron native bindings](https://www.electronjs.org/docs/latest/development/creating-api),
[process model](https://www.electronjs.org/docs/latest/tutorial/process-model),
[Node subprocesses](https://nodejs.org/api/child_process.html),
[pywebview bridge](https://pywebview.flowrl.com/guide/interdomain),
[pywebview engines](https://pywebview.flowrl.com/guide/web_engine),
[Qt WebEngine architecture](https://doc.qt.io/qt-6/qtwebengine-overview.html), and
[PySide6 bindings](https://doc.qt.io/qtforpython-6/PySide6/QtWebEngineWidgets/index.html).

A possible Pyrolyze browser backend would preserve Python authoring and reactive
execution, send batched UI updates to a JavaScript DOM adapter, and route user
events back to Python. React is not inherently required. Python browser-host
bindings do not imply direct Python access to DOM objects; Qt WebEngine normally
uses injected JavaScript for page manipulation.

## Decisions And Deferrals

- Continue proving the existing Pyrolyze model; do not broaden this discussion
  into a performance rewrite or a new browser backend now.
- Keep confirmed defects, suspected defects, and unmeasured opportunities distinct.
- Preserve native fidelity and escape hatches when improving the common API.
- Revisit browser hosting, broader portability, and Rust only as separately scoped
  work when there is a concrete application or measurement motivating it.
- No rendering implementation changes or fresh end-to-end benchmarks were made
  as part of this discussion report.
