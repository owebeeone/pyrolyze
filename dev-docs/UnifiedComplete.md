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

### Phase tracker

| Phase | Status | Notes |
| --- | --- | --- |
| **0** — Scope and governance | **Done** | `unified_native_coverage.json`, `UNIFIED_NATIVE_API_VERSION`, open decisions resolved. |
| **1** — Inventory and normalization | **Done (Wave A)** | `wave_a_param_mapping.json`; full per-widget `widget_catalog_unified.json` + DPG dump merge still optional/future. |
| **2** — Mount points and shell | **Done** | `MountKeys.md`, `ReferenceShellLayout.md`, `pyrolyze.unified.mount_keys`, schema tests, cross-links, `tests/unified/e2e/test_reference_shell_layout.py` (Qt / Tk / DPG). |
| **3** — Unified API design | **Done (Wave A)** | `docs/reference/Unified_Native_Methods.md`; typed `qt=` / `tk=` / `dpg=` bags and error policy still to tighten. |
| **4** — Implementation waves | **Done (Waves A–D)** | `UnifiedNativeLibrary` through `spacer`; tests in `tests/unified/test_unified_native_library.py`; `waves_bcd_param_mapping.json`; coverage script updated. |
| **5** — Testing and parity | **Done** | Emitter matrix + push_button smoke + mount-key routing (Qt/Tk/DPG); Tk ``MountableEngine`` skips on macOS when mixed with Qt; run ``tests/unified/`` on Linux CI for full Tk coverage. |
| **6** — Policy and cutover | **Done** | `pyrolyze.unified.context_keys`; subtree override tests (`test_phase6_app_context.py`); `examples/unified_hello_pyside6.py`; `scripts/check_unified_drift.py` + AST drift test; `Public_API_Surface.md` unified section. |

---

## Phase 0 — Scope and governance

**Status: Done**

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

**Implemented:** run `scripts/extract_widget_catalogs.py` then
`scripts/build_unified_coverage.py` →
`dev-docs/widget-reconcile/unified_native_coverage.json`. API version:
`pyrolyze.unified.UNIFIED_NATIVE_API_VERSION`.

---

## Phase 1 — Mechanical inventory and normalization

**Status: Done (Wave A deliverables)** — full per-entry constructor/mount schema file still future work.

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

**Status: Done** — canonical keys, `MountKeys.md`, **`ReferenceShellLayout.md`**, **`tests/unified/e2e/test_reference_shell_layout.py`** (same `mount_keys` advert sequence on Qt, Tk, DPG), and **ReactiveRootWindowProxy** cross-links.

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

Consolidated in **`dev-docs/ReferenceShellLayout.md`** (mermaid tree + tables).

### 2.3 Reference layouts

- **Implemented:** `tests/unified/e2e/test_reference_shell_layout.py` — three
  cases (Qt / Tk / DPG) share the same `mount_keys` advert sequence and
  `with host():` shape; host `kind` and `target=` selectors follow
  `ReferenceShellLayout.md`.

**Exit criteria**

- Mount key list frozen.
- Three reference tests (or examples) green.
- Cross-link from `dev-docs/ReactiveRootWindowProxy.md` where window lifetime
  intersects shell APIs.

---

## Phase 3 — Unified API design (identical author surface)

**Status: Done (Wave A)** — method list published; `qt=` / `tk=` / `dpg=` typed extras and formal `NotImplementedError` matrix still optional follow-up.

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

**Status: Waves A–D complete** — see `docs/reference/Unified_Native_Methods.md`,
`waves_bcd_param_mapping.json`, and `tests/unified/test_unified_native_library.py`.
File dialogs, plots, and node-editor surfaces remain **deferred** (toolkit-native
or a future scoped module per Wave D plan).

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

**Per-wave checklist (Wave A)**

- [x] Abstract method(s) on `UnifiedNativeLibrary` (or shell facet)
- [x] `QtUnifiedNativeLibrary` / `TkUnifiedNativeLibrary` /
      `DpgUnifiedNativeLibrary` implementations
- [x] Unit tests: expected `UIElement(kind=..., props=...)` per backend
- [ ] Behavior matrix row updated (short prose on known differences) — optional prose in `RoleMatrix` / coverage JSON notes

---

## Phase 5 — Testing and parity discipline

**Status: Done** — see `tests/unified/test_phase5_*.py`, `tests/unified/conftest.py`.

### 5.1 Unit matrix

- **Shipped:** `tests/unified/test_unified_native_library.py` (exact ``UIElement`` per
  method) plus **`test_phase5_emitter_matrix.py`**: every emitter mounted once per
  backend via ``MountableEngine`` (structural acceptance).
- Optional follow-up: golden **props** JSON for large payloads.

### 5.2 Behavioral smoke

- **Shipped:** `tests/unified/test_phase5_behavior_smoke.py` — ``push_button`` through
  each backend’s ``MountableEngine`` (native instance created). Full event-loop
  interaction remains a future harness upgrade.

### 5.3 Mount integration

- **Shipped:** `tests/unified/test_phase5_mount_routing.py` — ``mount_key(shell.body)``
  resolves through ``PyrolyzeMountAdvertisement`` to native selectors (Qt
  ``central_widget``, Tk ``pack`` mount point, DPG ``standard`` on ``DpgWindow``).
- Phase 2 advert graph: `tests/unified/e2e/test_reference_shell_layout.py`.

### 5.4 CI

- **Command:** from the ``pyrolyze`` repo root, ``uv run pytest tests/unified/`` (or
  full ``uv run pytest``). Prefer **Linux** agents so Tk ``MountableEngine`` tests
  run (they are **skipped on macOS** in ``conftest.py`` because ``Tk()`` after
  PySide6 in the same process aborts on Darwin).
- **Lazy imports:** ``pyrolyze.unified`` re-exports adapters via ``__getattr__`` and
  ``get_unified_native_library`` loads **one** backend so optional tooling can
  avoid pulling Qt when only Tk/DPG is needed.

**Exit criteria**

- Every unified method row has **at least one test** per applicable backend
  (emitter matrix + existing equality tests).
- Mount reference tests green; engine-level routing covered by Phase 5.3 tests.

---

## Phase 6 — Policy, examples, and cutover

**Status: Done**

Canonical **theme / density / typography** keys, drift guards, public reference
prose for `pyrolyze.unified`, and a PySide6 hello example are in place. Mount
resolution still does **not** read authored app context; authors use
`use_app_context` / `get_authored_app_context` (or equivalent) and map values into
unified emitter arguments or `UIElement` props—see
`src/pyrolyze/unified/context_keys.py` and
`dev-docs/HierarchicalContextManagementPlan.md`.

### 6.1 App context

- **Shipped:** `pyrolyze.unified.context_keys` — `UNIFIED_THEME`, `UNIFIED_DENSITY`,
  `UNIFIED_TYPOGRAPHY` (`AppContextKey` instances with stable debug names).
- **Shipped:** `tests/unified/test_phase6_app_context.py` — for **Qt, Tk, and DPG**,
  a subtree `open_app_context_override` supplies a value that is read with
  `get_authored_app_context` and passed into a unified emitter; `MountableEngine`
  mounts the resulting `UIElement` and asserts native-facing props (Tk skips on
  macOS per `conftest.py`).

### 6.2 Documentation and examples

- **Shipped:** `docs/reference/Public_API_Surface.md` — **Portable native surface
  (`pyrolyze.unified`)** section (`get_unified_native_library`, `mount_keys`,
  `context_keys`, pointer to `Unified_Native_Methods.md`, generated libraries as
  advanced escape hatch).
- **Shipped:** `examples/unified_hello_pyside6.py` (runner:
  `examples/run_unified_hello_pyside6.py`).

### 6.3 Drift prevention

- **Shipped:** `scripts/check_unified_drift.py` — no disallowed
  `backends.common`-style drift.
- **Shipped:** `tests/unified/test_phase6_drift_guard.py` — AST guard on forbidden
  references (aligns with `dev-docs/WidgetReconcilePlan.md` direction).

**Exit criteria (Phase 6)**

- [x] Stable context keys for unified authoring.
- [x] Per-backend test proving subtree overrides can influence values fed into
  unified emitters and through mount.
- [x] Public API doc + drift checks + at least one runnable unified example.

### Phase 6 follow-ups (optional, not Phase 6 blockers)

- **Examples:** migrate **additional** repo examples off ad hoc `call_native`
  wherever `pyrolyze.unified` already covers the widget (hello is the baseline,
  not full migration).
- **Deeper coupling (only if product asks):** today emitters do not implicitly
  call `use_app_context` inside library code; any automatic read inside
  `UnifiedNativeLibrary` would be a separate, explicit API/design change.

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

- `src/pyrolyze/unified/` — implementation package (includes `context_keys.py`)
- `scripts/check_unified_drift.py` — no `backends.common` drift
- `tests/unified/` — tests mirroring the package
- `dev-docs/UnifiedMountBasedNativeApi.md` — design intent
- `dev-docs/widget-reconcile/RoleMatrix.md` — role → name proposals
- `dev-docs/unified_plan/` — per-backend implementation notes
- `dev-docs/ReactiveRootWindowProxy.md` — shell / window lifetime

---

## Open decisions (record resolutions here)

| Topic | Options | Resolution |
| --- | --- | --- |
| Monolith vs sub-facades | Single class vs `shell` / `widgets` split | **Wave A:** single `UnifiedNativeLibrary`; add `unified.shell` only when window/dialog methods land. |
| DPG plots in v1 | Unified subset vs `unified.dpg` only | **Defer:** no unified plot API in v1; use `call_native` / generated DPG. |
| `label` | Always `pyrolyze.api.Label` vs per-backend native label | **`pyrolyze.api.Label`** for portable semantic label until native styling is required. |
| File dialog shape | Sync vs async callback API | **Defer** to Phase C; no unified `file_dialog` in Wave A. |

---

## Document history

- **Created** as the actionable completion plan for full native coverage under
  `pyrolyze.unified`, aligned with existing reconcile and mount docs.
- **Updated** — phase tracker and per-phase status lines after Phases 0–4 (Wave A)
  land in code and docs.
- **Updated** — Phase 6 marked done (context keys, drift script, public API doc,
  PySide6 unified hello example).
- **Updated** — Phase 6 body reconciled with the phase tracker: detailed **Done**
  checklist, accurate semantics (authors map context into emitters; mount does
  not read authored context), and **Phase 6 follow-ups** for optional example
  migration / future auto-read design.
