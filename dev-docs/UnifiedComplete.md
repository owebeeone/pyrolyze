# Unified native API — complete surface plan

## Purpose

This document is the **execution plan** for growing `pyrolyze.unified` into a
**full-coverage** author surface over the three first-class backends (PySide6,
Tkinter, Dear PyGui): **best-effort identical** Python API (names and shared
parameters), **aligned mount semantics**, and **documented** gaps where
toolkits cannot match.

It complements:

- `dev-docs/UnifiedMountBasedNativeApi.md` — architecture and goals
- `dev-docs/widget-reconcile/RoleMatrix.md` — role triage and proposed unified names
- `dev-docs/unified_plan/README.md` — per-backend notes

**North star:** one primary facade (and optional sub-facades if the surface is
large), same method names on every backend, shared keyword parameters where
meaning exists, optional `qt=` / `tk=` / `dpg=` bags for unavoidable extras, and
canonical **mount keys** with per-backend mapping recipes.

Literal behavioral parity (edge cases, modality, threading, pixels) is **not**
required; **identical API shape + a published behavior matrix** is.

---

## Phase 0 — Scope and governance

**Duration:** short if decisions are crisp; longer if the team debates every row.

### 0.1 Define “ALL native APIs”

- **Mechanical upper bound:** union of `kind` values in generated
  `UiInterface.entries` (Qt, Tk) plus Dear PyGui **`M_*` generated factories**
  **and** `backends/dearpygui/items.py` factories (two catalogs must both appear
  in the inventory).
- **Policy:** every catalog entry is exactly one of:
  - **Unified** — exposed as a named method (or grouped variant),
  - **Grouped** — one unified method with `variant=` / enum (avoid one method per Qt class),
  - **Excluded** — documented reason (Designer-only, duplicate, internal, defer to v2).

### 0.2 Classification rubric

Reuse and tighten the triage from `RoleMatrix.md`:

| Tag | Meaning |
| --- | --- |
| `portable` | Same unified name; acceptable parity |
| `best-effort` | Same unified name; documented semantic gaps |
| `toolkit-only` | No unified v1 API, or DPG-only module |

Add **parameter parity class** per method:

| Class | Meaning |
| --- | --- |
| `strict` | Shared params only; toolkit extras only via named bags |
| `coerced` | Shared param maps to different native shapes (document mapping) |
| `passthrough-heavy` | Rare; prefer not to unify without a strong use case |

### 0.3 API versioning

- Document a **`pyrolyze.unified` API version** (and optionally expose
  `UNIFIED_NATIVE_API_VERSION` in code) so apps can branch on supported methods.

**Exit criteria**

- One **coverage table** (checked-in JSON or spreadsheet exported to JSON) row
  per native entry: unified bucket, triage, exclusion reason, primary backend
  reference (`kind` or factory name).

---

## Phase 1 — Mechanical inventory and normalization

### 1.1 Regenerate and extend extracts

- Run and extend `scripts/extract_widget_catalogs.py` so DPG includes
  **`items.py`** alongside `M_*` (see `RoleMatrix.md` § Dear PyGui).
- When available, merge **DPG API dump** mountable metadata into the same schema.

### 1.2 Common schema

For each widget / factory, record at minimum:

- `backend`, `kind` or `factory` name
- Constructor / factory **parameters** (name, type, default)
- **Child policy** and **mount points** (from `UiWidgetSpec` and codegen where present)
- Link to **mounted type** / spec id for advanced users

**Artifact:** e.g. `dev-docs/widget-reconcile/widget_catalog_unified.json` (new
version or sibling of `widget_catalog_extract.json`).

### 1.3 Parameter harmonization

- Define a **canonical vocabulary**: `text`, `value`, `min`, `max`, `step`,
  `items`, `selected_index`, `enabled`, `visible`, etc.
- For each unified method, maintain a **three-column mapping**: canonical param
  → Qt prop → Tk prop → DPG prop (or “N/A”).
- If no shared meaning exists, **omit** from the unified signature; use toolkit
  bags only.

**Exit criteria**

- Machine-readable catalog checked in.
- First-pass **param mapping** for all Wave A methods (see Phase 4).

---

## Phase 2 — Mount points and shell

### 2.1 Canonical mount keys

- Add `dev-docs/MountKeys.md` and/or `pyrolyze.unified.mount_keys` (names TBD).
- Small, versioned set: e.g. `shell.body`, `shell.menu_bar`, `shell.status`,
  `dialog.actions`, …
- Per key: semantics, whether **default** adverts are expected, single vs
  multiple child rules.

### 2.2 Per-backend recipes

For each key, document the **recommended** pattern:

- Qt/Tk: `advertise_mount(..., target=<GeneratedUiLibrary.mounts....>)`
- DPG: viewport vs per-window menu bars, child windows, etc. (honest divergence)

### 2.3 Reference layouts

- One **minimal shell** per backend under `examples/` or
  `tests/unified/e2e/`: same mount keys and same component tree shape, three
  backends.

**Exit criteria**

- Mount key list frozen.
- Three reference tests (or examples) green.
- Cross-link from `dev-docs/ReactiveRootWindowProxy.md` where window lifetime
  intersects shell APIs.

---

## Phase 3 — Unified API design (identical author surface)

### 3.1 Facade decomposition

Avoid a single class with hundreds of methods if the catalog demands it:

| Facet | Responsibility |
| --- | --- |
| `UnifiedNativeLibrary` (core) | Leaf widgets + simple containers you commit to unifying |
| `unified.shell` (or sibling) | Windows, dialogs, menu chrome — ties mount keys + window proxy |
| `unified.dpg_extra` or **v2** | Plots, handlers, node editor — **explicit** non-parity or defer |

### 3.2 Signatures

- Prefer **keyword-only** parameters for the shared stem.
- Avoid bare `**kwargs` on the unified surface; use **`qt=` / `tk=` / `dpg=`**
  (or typed mappings) for extras.

### 3.3 Return type

- Prefer **`UIElement`** for consistency with `call_native` pipelines.
- Document methods that conceptually emit **fragments** (multiple logical
  roots) vs a single node.

### 3.4 Errors

- Unsupported combination → **`NotImplementedError`** (or structured error)
  naming `backend_id` and pointing to the behavior matrix.

**Exit criteria**

- Published **method list + signatures + triage** before mass implementation
  (can live in this file’s appendix or `docs/reference/`).

---

## Phase 4 — Implementation waves

Implement **backend adapters in lockstep** (Qt, Tk, DPG) per wave; no wave
merges without **green tests** on all three where the method is `portable` or
`best-effort`.

### Wave A — High reuse, lower controversy

From `RoleMatrix.md` and catalog coverage: e.g. combo, slider, int/float
fields, progress, tabs (subset), radio grouping patterns — prioritized by
**extract completeness** and **test simplicity**.

### Wave B — Text and structure

`text_area`, multiline vs rich text boundaries, label variants (resolve DPG
`add_text` vs widget-label semantics in the mapping table).

### Wave C — Chrome and system UI

Menu bars, toolbars (if in scope), file dialogs — often `best-effort` or
async-shaped APIs.

### Wave D — DPG-heavy / advanced

Plot series, custom handlers, node graphs — either a **unified subset** with
clear bounds or an explicit **`dpg`-scoped** extension module so Qt/Tk authors
are not misled.

**Per-wave checklist**

- [ ] Abstract method(s) on `UnifiedNativeLibrary` (or shell facet)
- [ ] `QtUnifiedNativeLibrary` / `TkUnifiedNativeLibrary` /
      `DpgUnifiedNativeLibrary` implementations
- [ ] Unit tests: expected `UIElement(kind=..., props=...)` per backend
- [ ] Behavior matrix row updated (short prose on known differences)

---

## Phase 5 — Testing and parity discipline

### 5.1 Unit matrix

For each unified method:

- Assert emitted **`UIElement`** shape per backend (pattern in
  `tests/unified/test_unified_native_library.py`).
- Optional: golden **props** JSON for large payloads.

### 5.2 Behavioral smoke

- Small set of **integration** tests per backend: mount + render + one
  interaction path where harness exists.
- Known differences called out in **test docstrings** and the behavior matrix.

### 5.3 Mount integration

- Same PyRolyze tree, three backends: identical **mount key** adverts; assert
  compatible routing within engine capabilities.

### 5.4 CI

- Run unified tests for **qt**, **tk**, **dpg** on every change; avoid silent
  backend skips unless CI truly cannot run a toolkit (document if so).

**Exit criteria**

- Every unified method row has **at least one test** per applicable backend.
- Mount reference tests green.

---

## Phase 6 — Policy, examples, and cutover

### 6.1 App context

- Define minimal **`AppContextKey`** set (theme, density, typography).
- Adapters **read** keys on create/update paths per
  `dev-docs/HierarchicalContextManagementPlan.md`.
- At least **one E2E per backend** with a subtree override affecting native
  output.

### 6.2 Documentation and examples

- Update `docs/reference/Public_API_Surface.md`: unified as default path;
  generated `*UiLibrary` as advanced.
- Migrate examples off ad hoc `call_native` where unified covers the widget.

### 6.3 Drift prevention

- CI grep: no reintroduction of deprecated **common**-style modules if removed
  (see `dev-docs/WidgetReconcilePlan.md` checklist).

**Exit criteria**

- Non-trivial sample app buildable using **unified + mount keys**, with
  **rare** `call_native` only for escapes.

---

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| DPG `M_*` vs `items.py` split | Merge catalogs in Phase 1; one adapter rule per kind; tests fail on wrong factory path |
| Same API hiding semantic mismatch | Behavior matrix + integration smokes; `NotImplementedError` where unsafe |
| Method explosion | Grouping (`variant=`, enums) + sub-facades; single **import root** (`pyrolyze.unified`) |
| Plot / advanced DPG scope creep | Explicit **v2** or `dpg` namespace; do not block Wave A–C |

---

## Related paths (repository-relative)

- `src/pyrolyze/unified/` — implementation package
- `tests/unified/` — tests mirroring the package
- `dev-docs/UnifiedMountBasedNativeApi.md` — design intent
- `dev-docs/widget-reconcile/RoleMatrix.md` — role → name proposals
- `dev-docs/unified_plan/` — per-backend implementation notes
- `dev-docs/ReactiveRootWindowProxy.md` — shell / window lifetime

---

## Open decisions (record resolutions here)

| Topic | Options | Resolution |
| --- | --- | --- |
| Monolith vs sub-facades | Single class vs `shell` / `widgets` split | _TBD_ |
| DPG plots in v1 | Unified subset vs `unified.dpg` only | _TBD_ |
| `label` | Always `pyrolyze.api.Label` vs per-backend native label | _TBD_ |
| File dialog shape | Sync vs async callback API | _TBD_ |

---

## Document history

- **Created** as the actionable completion plan for full native coverage under
  `pyrolyze.unified`, aligned with existing reconcile and mount docs.
