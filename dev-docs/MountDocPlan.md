# Mount and mount-advert documentation plan

This plan scopes **user-facing** and **contributor-facing** documentation for:

- explicit `mount(...)` (already partially documented)
- `advertise_mount(...)` and the mount-advertisement graph
- the **`pyrolyze.testing.generic_backend`** harness used to generate minimal PyRolyze UI libraries on the fly for tests

Design background remains in existing dev-docs (`MountableSpecModel.md`, `MountAdvertsDagBuilder.md`, `mount_advert_plan/`). This file answers **where** new prose should land, **why** authors care, and **how** behavior is grounded in tests and code.

---

## 1. Motivation (why authors care)

### 1.1 `mount(...)`

Already summarized in `docs/user/Mount_And_Mount_Points.md`: pick a backend attachment site when a parent exposes multiple mount points, or override generated default attach behavior.

### 1.2 `advertise_mount(...)`

**Problem:** Callers outside your component should not depend on your *internal* mount selectors (grid cells, notebook tabs, layout indices). Those names are often backend-specific, verbose, or unstable across refactors.

**What adverts do:** A container (native or semantic) **publishes a stable, public key** (string, enum-like value, or `mount_key(...)`) and maps it to one or more **internal** `SlotSelector` / `MountSelector` targets. Callers use `with mount(public_key):` (or multi-selector lists); the runtime resolves through the advertisement to the real attachment site.

**Concrete benefits:**

- **Stable API surface** for “slots” (e.g. `"body"`, `"sidebar"`) without leaking `Qt.mounts.widget(row=…)` into every caller.
- **`default=True`** marks which public advert should receive children when the caller does not use an explicit `mount(...)`—normalizing toolkit-specific default attach rules.
- **Keyed / remapping scenarios:** when public shape changes across rerenders (e.g. keyed loops), tests and implementation ensure advert metadata and legal public mount shapes stay consistent (`test_advertise_mount_anchor_order.py`, `test_generic_backend_mount_advert_remap.py`).
- **Composability:** adverts are retained at specific anchor sites in container child order; routing and reconciliation use the advert graph (`test_hydo_mount_advert_graph.py`, `test_mount_advert_routing_passthrough.py`).

User docs should lead with these outcomes; deep invariant lists stay in dev-docs or contributor material.

---

## 2. Where to add documentation

### 2.1 User docs (`docs/user/`)

| Target | Action |
|--------|--------|
| [`docs/user/Mount_And_Mount_Points.md`](../docs/user/Mount_And_Mount_Points.md) | **Extend** with a dedicated section *“Advertising mount points (`advertise_mount`)”*: motivation (above), minimal API shape (`key=` / `name=`, `target=`, positional selectors, `default=`), valid call patterns, relationship to `mount(...)` and `mount_key(...)`, and one short end-to-end example (generic or PySide6-style). Link to `dev-docs/MountAdvertsDagBuilder.md` for readers who want design history. |
| [`docs/user/Authoring_Overview.md`](../docs/user/Authoring_Overview.md) | **Optional short cross-link** in the section that discusses structure/containers—one paragraph + link to the mount doc, if that file already mentions composition. |
| [`docs/user/Building_A_UI_Library.md`](../docs/user/Building_A_UI_Library.md) | **Optional** note for library authors: when exposing multiple attach sites, consider adverts for stable names; point to the same mount user doc. |

### 2.2 Reference (`docs/reference/`)

| Target | Action |
|--------|--------|
| [`docs/reference/Public_API_Surface.md`](../docs/reference/Public_API_Surface.md) | **Sync with** `src/pyrolyze/api.py` `__all__`: add `advertise_mount`, `mount_key`, `MountKeySelector`, `PyrolyzeMountAdvertisement`, `PyrolyzeMountAdvertisementRequest` (and any other mount-related exports already missing). Keep this list mechanical—one line per symbol, grouped under a small “Mount surface” subsection. |

### 2.3 Glossary (`docs/reference/`)

| Target | Action |
|--------|--------|
| [`docs/reference/Glossary.md`](../docs/reference/Glossary.md) | **Add entries** if present in the tree: *mount advertisement*, *public mount key*, *default advert*, *mount directive* (if not already defined). Keep definitions short; link to `Mount_And_Mount_Points.md`. |

### 2.4 Design docs (`docs/design/`)

| Target | Action |
|--------|--------|
| Optional | Only if we want a **single** design-page pointer for “advert graph + reconciler”: a short subsection in [`docs/design/Reconciler_And_UI_Node_Model.md`](../docs/design/Reconciler_And_UI_Node_Model.md) or [`docs/design/Runtime_Context_Graph.md`](../docs/design/Runtime_Context_Graph.md) with a link to `dev-docs/MountAdvertsDagBuilder.md`. **Not required** for MVP user understanding. |

### 2.5 Contributor docs (`docs/contributor/`) — generic backend framework

The on-the-fly API generation for tests lives in `src/pyrolyze/testing/generic_backend/`. It deserves **its own** contributor page (not buried in mount-only prose).

| Target | Action |
|--------|--------|
| **New:** `docs/contributor/Generic_Backend_Testing.md` | **Create** as the home for: purpose (minimal generated `@pyrolyze` components + mounts without a full PySide6/tkinter library), the spec model (`NodeGenSpec`, `MountSpec`, `ParamSpec`, `MountInterfaceKind`), `BuildPyroNodeBackend` (`source_module_text`, `source_namespace`, `pyro_func`, `engine`, `context`), `PyroNodeEngine`, `PyroRenderHarness`, snapshot helpers (`run_pyro`, `run_pyro_ui`), and `PyrolyzeMountCompatibilityError`. Include a **minimal worked example** mirroring `tests/test_generic_backend_api.py` or `test_generic_backend_harness.py`. |
| [`docs/user/Testing_Pyrolyze_Code.md`](../docs/user/Testing_Pyrolyze_Code.md) | **Add a bullet** under “Useful places” / integrated tests: mount-advert and dynamic mount behavior often use `pyrolyze.testing.generic_backend`; link to `../contributor/Generic_Backend_Testing.md`. |
| [`docs/contributor/README.md`](../docs/contributor/README.md) | **Index link** to the new page if the contributor README lists documents by topic. |

[`AGENTS.md`](../AGENTS.md) already tells contributors to prefer this framework for certain tests; the new contributor doc is the **expandable** reference that `AGENTS.md` can cite in one sentence.

### 2.6 Examples (`examples/`)

Optional follow-up: a small **checked-in** example (or extension of an existing grid example) that uses `advertise_mount` in author-facing form, **if** we want parity with `scratch/advertise_mount_example.py` without pointing users at `scratch/`. Track separately—examples are higher ceremony than docs-only work.

---

## 3. How it works (documentation outline, grounded in code and tests)

When writing user-facing prose, the following is the **intended mental model**; details should be trimmed for `docs/user/` and expanded only where helpful.

### 3.1 API and lowering

- `advertise_mount` is a `@pyrolyze_slotted` helper in [`src/pyrolyze/api.py`](../src/pyrolyze/api.py). At compile time it lowers like other slotted calls (plain-call slot); at author level it returns a `PyrolyzeMountAdvertisementRequest` describing **key**, **selector tuple**, and **default** flag.
- Runtime resolves requests into retained **`PyrolyzeMountAdvertisement`** values (with slot and surface-owner identity) attached in the emitted tree. See `tests/test_mount_advert_api.py` for request shape, transform visibility, and `RenderContext.debug_mount_advertisements()`.

### 3.2 Ownership and placement rules

- Adverts must bind to a **native container** render context; invalid placement is rejected (`tests/test_mount_advert_binding.py`).
- **Anchor order:** adverts are retained at exact call sites in container child order; rerenders update key mapping where legal (`tests/test_advertise_mount_anchor_order.py`).

### 3.3 Routing and graph behavior

- Passthrough and routing behavior: `tests/test_mount_advert_routing_passthrough.py`.
- Hydo / advert graph stability: `tests/test_hydo_mount_advert_graph.py`.

### 3.4 Generic backend: mount + advert integration

The generic backend drives **real** compile + runtime paths using **generated** source from [`specs.py`](../src/pyrolyze/testing/generic_backend/specs.py) and [`sourcegen.py`](../src/pyrolyze/testing/generic_backend/sourcegen.py). Tests to cite when documenting behavior:

| Concern | Primary tests |
|--------|------------------|
| Spec validation / model | `tests/test_generic_backend_specs.py`, `test_generic_backend_model.py` |
| Source generation | `tests/test_generic_backend_sourcegen.py`, `test_generic_backend_generation.py` |
| Harness + rerender | `tests/test_generic_backend_harness.py`, `test_generic_backend_runtime.py` |
| Selector families / branching | `tests/test_generic_backend_mount_selector_families.py`, `test_generic_backend_mount_branching.py` |
| Adapter replay | `tests/test_generic_backend_mount_adapter_replay.py` |
| Compatibility errors | `tests/test_generic_backend_mount_compatibility.py` |
| Advert readability / stress / rotation / remap | `tests/test_generic_backend_mount_advert_readable.py`, `test_generic_backend_mount_advert_stress.py`, `test_generic_backend_mount_advert_rotation.py`, `test_generic_backend_mount_advert_remap.py` |
| Snapshots | `tests/test_generic_backend_snapshots.py` |

End-to-end generated mountable engine coverage (if documented as related): `tests/test_generated_hydo_mountable_engine.py`.

### 3.5 Imported helpers returning advert requests

- Compiler detection of return-typed mount-advert helpers: `tests/test_mount_advert_api.py` (`imported_advert_request` / `pyrolyze_testsupport.imported_annotations`).

---

## 4. Suggested writing order

1. Update **`Public_API_Surface.md`** (quick win, reduces drift).
2. Extend **`Mount_And_Mount_Points.md`** with the `advertise_mount` section and examples.
3. Add **`docs/contributor/Generic_Backend_Testing.md`** and wire links from `Testing_Pyrolyze_Code.md` and contributor README.
4. **Glossary** entries and optional design cross-links as time allows.

---

## 5. Non-goals (this plan)

- Duplicating the full `MountableSpec` type dump from `MountableSpecModel.md` into user docs.
- Replacing existing mount-advert design plans under `dev-docs/mount_advert_plan/`; user docs should **link** there for history and rationale.
- Documenting `scratch/` examples as stable user entry points.
