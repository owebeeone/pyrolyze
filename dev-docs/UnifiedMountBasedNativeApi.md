# Unified Mount-Based Native API

## Purpose

PyRolyze today ships three first-class native toolkit integrations under
`src/pyrolyze/backends/` (Dear PyGui, PySide6, Tkinter) plus a small shared
semantic surface in `src/pyrolyze/backends/common/` (`CoreUiLibrary` and related
helpers). That common layer predates stable **`mount(...)`** and
**`advertise_mount(...)`** and encodes a single frozen set of semantic kinds
(section, row, button, …) that does not emerge from mount points or from
toolkit-specific layout.

This document proposes replacing that bespoke “common backend” pattern with a
**unified author-facing library** that:

1. **Names stable mount roles** (public keys) and maps them to toolkit-native
   targets via `advertise_mount(...)`.
2. **Exposes one consistent Python API surface** (function and type names) for
   authors, implemented per toolkit by thin **adapters** that share identical
   public names for the same semantic operations.
3. **Composes with hierarchical app context** (`app_context_override` /
   `use_app_context`) so cross-cutting policies—theme, density, font scale,
   locale-affected formatting—apply to a **class** of native operations at once
   without prop drilling through every widget call.

Detailed alignment of the three underlying APIs is **out of scope for this
document**; the next step is a deliberate inventory of each toolkit’s generated
library and mount specs, then filling in adapter bodies and documenting
intentional cheats where no portable equivalent exists.

**There is no backwards-compatibility requirement** for the current
`backends/common/` surface. Once the unified mount-based library and adapters
work for the supported workflows, **`src/pyrolyze/backends/common/` is deleted**
(along with any imports and tests that depended on it), rather than kept on a
deprecation path.


## Problem

- **`CoreUiLibrary` is a parallel UI model.** It does not route through the
  same mount-advertisement graph that real apps use for shell regions (menu
  bar, body, side panes, dialogs).
- **Semantic duplication.** Authors may need both toolkit-specific layout
  (`Qt.mounts.*`, DPG/Tk mount selectors) and common helpers, with unclear
  ownership of “where content lands.”
- **Cross-cutting styling and sizing** differ wildly per toolkit (Qt stylesheets
  vs Tk `option_add` / ttk themes vs DPG themes). Without a shared **policy**
  layer, every example and library reinvents ad hoc threading of theme state.
- **Naming drift risk.** If each backend exposes different helper names for the
  same idea (“primary button”, “dense spacing”), portable mental models and
  docs suffer.


## Goals

- **Mount-first composition:** The unified library’s shell and extension points
  are expressed as **advertised mount keys** with documented meanings, not as
  hidden singleton registries inside `common/`.
- **Identical public adapter names:** For each supported unified operation, all
  three backends expose the **same** function, class, or module attribute names
  (same spelling and rough signature shape). Implementation may differ; names
  must not.
- **App-context–driven policy:** Define a small set of **`AppContextKey`**
  values (or one structured key) for presentation policy. Adapters read those
  keys when applying theme, default sizes, or typography so a subtree override
  affects every native call in that subtree consistently.
- **Explicit impossibility:** Where a capability cannot be unified, the design
  documents a **single** escape hatch (e.g. toolkit-only module, or a unified
  function that raises `NotImplementedError` on unsupported backends) rather than
  silent divergence.


## Design priorities

The unified layer is **not** primarily a promise that every backend behaves the
same. The main wins are:

- **A pleasant author surface** for the **common stem** of UI work (labels,
  fields, toggles, simple layout hooks, shell mount keys)—fewer names to learn,
  less boilerplate than always calling generated libraries directly.
- **Composition:** unified pieces combine with **`mount` / `advertise_mount`**
  and with **native** widgets from the generated libraries in the same tree, so
  teams can **mix and match** (unified where it helps, native where it does not).
- **Shared vocabulary:** identical **adapter names** across backends support
  reading, teaching, and optional multi-backend apps—even when behavior is
  **best-effort** or toolkit-specific details differ.

**Strict cross-toolkit compatibility** (same semantics, same edge cases) is a
**secondary** goal: valuable where cheap, documented honestly where not. The
**role triage** in `dev-docs/widget-reconcile/RoleMatrix.md` (portable /
best-effort / toolkit-only) stays the honest contract; “nice API + composition”
comes first.


## Non-Goals

- Preserving or migrating authors off `CoreUiLibrary` gradually; the old common
  layer is removed in one cut when the replacement is ready.
- Replacing generated per-toolkit libraries or mount selector types; those
  remain the source of truth for **native** placement.
- **Requiring** uniform behavior across Qt, Tk, and DPG for every unified entry;
  parity is pursued only where it does not block a good default API.
- A pixel-perfect single theme across Qt, Tk, and DPG.
- GRIP-specific transport APIs (GRIP may consume the same app-context keys, but
  this doc stays PyRolyze-native).


## Related documents

- `dev-docs/WidgetReconcilePlan.md` — widget inventory methodology, phased
  deliverables, and acceptance criteria.
- `dev-docs/widget-reconcile/README.md` — mechanical extracts (`widget_catalog_extract.json`, `surface_analysis.json`) and role triage (`RoleMatrix.md`, `AdditionalAnalysis.md`).
- `dev-docs/unified_plan/README.md` — per-backend implementation plans (PySide6, Tkinter, DearPyGui).
- `dev-docs/ReactiveRootWindowProxy.md` — reactive root and **window proxies**
  for toolkit-owned window lifetime (complements mount-based interior layout).


## Conceptual Architecture

### 1. Layered surfaces

| Layer | Responsibility |
| --- | --- |
| **Unified library** (new) | **Facade class** (shared abstract base + concrete backends) exposing the same method names as today’s generated `*UiLibrary` pattern; stable mount-key helpers; optional semantic `UIElement` factories. |
| **Per-toolkit adapter class** | Concrete subclass of the unified base (Qt / Tk / DPG); maps each unified operation to the generated native library and mounts; reads app context when applying policy. |
| **Existing generated libraries** | Low-level kinds, props, `*.mounts.*` selectors; unchanged except where adapters need small, justified hooks. |

The unified library **depends on** mount advertisement at composition sites
(e.g. a layout component that `advertise_mount("body", target=...)` and
children that `mount("body", ...)`), not on `CoreUiLibrary` owning layout by
itself.

### 2. Mount keys as the public contract

- **Canonical mount key set:** A small, versioned enumeration of string keys
  (or `mount_key(...)` factories) documented in one place: e.g. `shell.body`,
  `shell.chrome`, `dialog.footer`—exact names to be chosen during API inventory.
- **Toolkit mapping:** Each backend ships a **mapping table** or helper module
  that, for each canonical key, documents the recommended
  `advertise_mount(..., target=Native.mounts....)` pattern for typical shells
  (grid window, DPG viewport, Tk frame hierarchy).
- **Defaults:** Use `default=True` on adverts where the design calls for a
  fallback mount target when the author does not override the key (same
  semantics as today’s `advertise_mount`).

### 3. Adapter naming rules

- **Package (implemented):** `pyrolyze.unified` under `src/pyrolyze/unified/`, with
  modules `qt.py`, `tk.py`, `dpg.py`, `factory.py`, and `base.py`.
- **Mandatory:** For every unified operation, the three concrete classes expose
  the **same method names** (and roughly the same signatures on the shared
  parameters) with documented differences on extras.
- **Types:** Shared **protocols** or an **abstract base class** in a
  toolkit-agnostic module; concrete return types may remain toolkit-specific
  where needed, but the **operation name** stays unified.
- **Cheats:** When only one toolkit supports an operation, either omit from the
  unified surface until a second backend can implement it, or provide a unified
  stub that documents the limitation and fails fast in unsupported environments.

### 4. Class-based adapters and runtime backend selection

Mirror the **generated UI library pattern** (`PySide6UiLibrary`, …): a **single
facade type** authors hold onto, backed by a **unified abstract base** (ABC or
`typing.Protocol`) plus **one concrete subclass per toolkit**. Each concrete
class implements the same unified methods and owns references to the matching
generated `*UiLibrary` (for `call_native`, `*.mounts.*`, kinds).

**Why classes (not only flat module functions):**

- **Runtime swap:** process startup (or test fixture) chooses the backend via
  **environment variable** and/or **CLI flag**, constructs the matching
  concrete class, and passes it as the unified base type everywhere else—same
  pattern as selecting a toolkit-specific library today, but with one stable
  author import.
- **Discovery:** optional registry `{name: type[UnifiedNativeLibrary]}` for
  `--backend=qt` style CLIs.
- **Extension:** optional `qt=`, `tk=`, `dpg=` passthrough bags can live on the
  base API without duplicating module-level function sprawl.

**Selection (implemented):**

- Environment variable **`PYROLYZE_UNIFIED_BACKEND`**: values `qt` (default), `tk`,
  `dpg` (case-insensitive; stripped).
- **`get_unified_native_library(backend=None)`** in `pyrolyze.unified`: uses
  the env var when ``backend`` is omitted; explicit ``backend`` overrides env.
- CLI entrypoints may set the same variable before import.

Authors type against the **base** / protocol; tests can inject a fake subclass
without importing Qt.


## App Context Integration

Hierarchical app context (see `dev-docs/HierarchicalContextManagementPlan.md`
and `dev-docs/HierarchicalContextManagement.md`) is the right place to hang
**presentation policy** that should affect many native calls:

- **Theme token bundle:** e.g. semantic colors (`surface`, `accent`), spacing
  scale, corner radius policy—not necessarily identical pixels across toolkits.
- **Density / size class:** compact vs comfortable; drives default padding,
  min sizes, and font step where the toolkit allows.
- **Typography scale:** a single multiplier or discrete step read by adapters
  when setting font sizes (mapping to `QFont`, Tk font tuples, DPG font/theme
  hooks).

### Usage pattern (author-facing)

- Root or subtree: `with app_context_override[THEME_KEY, DENSITY_KEY](...):`
- Inside unified helpers or generated wrappers: `use_app_context(THEME_KEY)` (or
  equivalent) so reactive invalidation re-applies native appearance when
  policy changes.

### Design constraints

- **Mount resolution does not read app context** (per existing hierarchical
  context plan); policy applies when **creating or updating** native widgets,
  not when resolving mount selectors.
- **Keys are declared once** in a small `unified` policy module so GRIP and
  hand-authored apps share the same identifiers.


## Relationship to `backends/common/`

The `backends/common/` package exists only until the unified library ships.

- Before deletion, move anything that must stay toolkit-agnostic (shared types,
  protocols, policy key declarations) into the new unified package or into
  existing shared modules such as `backends/model.py`—not into a second UI
  library.
- When the unified surface covers the intended examples and tests, **delete**
  `src/pyrolyze/backends/common/` and update all call sites in one pass.

Authors then use **one** high-level unified import for portable patterns;
toolkit-specific code uses the generated native library only when drilling into
native behavior.


## Tests, layout, and `.venv` import hook

### Test package layout

Mirror the unified **source** tree under `tests/` so paths stay obvious and
`pytest` collection stays predictable. Example (adjust to the final package
choice):

- `src/pyrolyze/unified/...` → `tests/unified/...`
- Per-backend adapters under parallel subtrees, e.g. `tests/unified/native/`
  with `test_qt_*.py`, `test_tk_*.py`, `test_dpg_*.py` aligned with adapter
  modules.

Narrow **unit** tests may stay adjacent to a single module when clearer; **end-to-end**
tests that exercise `@pyrolyze`, mounts, or adverts should follow
`AGENTS.md`—prefer `pyrolyze.testing.generic_backend` when it clarifies the
scenario.

### Prefer native PyRolyze code in tests

Where behavior is **author-visible** (components, mounts, context), tests
should use **public** PyRolyze source forms (`@pyrolyze`, `call_native(...)`,
`advertise_mount`, `mount`, …), not compiler-internal `__pyr_*` names—same rule as
hand-written examples (`pyrolyze/AGENTS.md`). How that source is **loaded** is
governed by the strategy below.

### Import hook under `pytest` and the venv

The public `pyrolyze` decorator in `pyrolyze.api` is still a **stub** for modules
that are **not** compiled. For on-disk code, transformation is triggered by a
**`#@pyrolyze` marker** in the first two lines of the module (same rule as
`should_transform_module` in the AST kernel).

- **Pytest:** the package registers **`project.entry-points.pytest11`** →
  `pyrolyze.compiler.pytest_plugin`, which calls
  `pyrolyze.compiler.import_hook.install()` during `pytest_configure`. `install`
  re-orders the finder to `sys.meta_path[0]` **after** pytest’s assertion rewrite
  hook is installed, so PyRolyze compilation runs first. Normal `uv run pytest …`
  loads `#@pyrolyze` test modules without extra steps. Example:
  `tests/unified/test_pyrolyze_compilation_runs_under_pytest.py`.
- **Plain `python` in a venv:** run **`uv run pyrolyze-import-hook-pth install`** once
  per environment; it writes `pyrolyze_import_hook.pth` under `site-packages`
  (path comes from `sysconfig`, no absolute paths in the repo). Use
  **`pyrolyze-import-hook-pth remove`** to delete that file. Implementation:
  `src/pyrolyze/pyrolyze_tools/import_hook_pth.py`.

### When to keep `load_transformed_namespace`

Use **`pyrolyze.compiler.load_transformed_namespace`** when the PyRolyze source
is a **string** built at test time (f-strings with generated `module_name`,
virtual filenames, or golden snapshots). Generic backend harnesses and several
compiler integration tests rely on this. Author-shaped snippets still use
`@pyrolyze` **inside** the string; only the loader differs.


## Implementation Phases

### Phase A — Inventory (next detailed pass)

- For each backend, list: mount selectors, container kinds, styling hooks
  (`AccessorKind` in `backends/model.py` is a useful index: `QT_PROPERTY`,
  `TK_CONFIG`, `DPG_CONFIG`, etc.).
- Mark each capability: **portable**, **best-effort**, **toolkit-only**.
- Produce a table of proposed **unified names** ↔ three implementations.

### Phase B — Mount contract

- Freeze the **canonical mount key** list and document each key’s meaning.
- Add one **reference layout** per toolkit in `examples/` or tests that uses
  only `advertise_mount` + `mount` for shell regions (can extend existing
  PySide6 grid example pattern).

### Phase C — Adapter skeleton

- Add the shared namespace, **unified base**, three **concrete adapter classes**,
  and **backend factory** (env/CLI); **identical method names** on the classes;
  implement stubs or narrow subset first; run tests on each backend matrix slice.

### Phase D — App context keys

- Define `AppContextKey` instances for theme/density/typography (minimal set).
- Wire one end-to-end scenario per toolkit: override at a subtree boundary and
  observe native widgets update reactively.

### Phase E — Cutover and docs

- Update contributor docs and examples to the unified library + adapters only.
- **Delete** `src/pyrolyze/backends/common/` and fix imports/tests; no
  compatibility shims.


## Risks and Mitigations

| Risk | Mitigation |
| --- | --- |
| False equivalence (same name, very different behavior) | Document behavior matrix; prefer narrow unified API over misleading parity. |
| App context + native side effects | Keep policy application in adapter code paths that already run on commit/update; avoid hidden global toolkit state. |
| Explosion of mount keys | Keep the canonical set small; use hierarchical context for variation instead of new keys per theme. |


## Open Questions

- Whether selection may be **rebound** after first `get_unified_native_library`
  call (today: factory returns a **new** instance each time; no global singleton).
- **CLI** flag naming in apps that wrap PyRolyze (library only defines env + API).
- How the **PyRolyze import hook** is enabled automatically for **`pytest`** runs
  from the project **`.venv`** (implementation TBD; see § Tests, layout, and
  `.venv` import hook).
- Whether some unified factories remain `@ui_interface` classes or become plain
  modules; either works if mount advertisement and naming rules are consistent.
- How grip-pyrolyze (if present in sibling repos) should **bootstrap** the same
  keys—coordinate in a follow-up doc if needed.


## Exit Criteria (for this design phase)

- This document reviewed and accepted as the direction of travel.
- Phase A inventory scheduled with explicit owners per toolkit.

**Exit criteria for removing `common/`:** unified library + three adapters
satisfy the agreed test and example set; then Phase E deletes `backends/common/`
with no deprecation period.
