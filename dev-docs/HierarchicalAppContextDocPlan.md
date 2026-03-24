# Hierarchical app context — documentation plan

This plan scopes **user-facing**, **reference**, and **maintainer** documentation
for subtree-scoped **authored** app context: `app_context_override[...](...)`
and `use_app_context(key)`.

Design rationale and phased implementation live in:

- [`HierarchicalContextManagement.md`](HierarchicalContextManagement.md)
- [`HierarchicalContextManagementPlan.md`](HierarchicalContextManagementPlan.md)

This file answers **where** to publish prose after behavior is stable, **why**
authors should use it, and **which tests** ground the “how it works” sections.

---

## 1. Motivation (user-facing summary)

### 1.1 Problem

PyRolyze still has a **root-scoped** internal app-context store (`AppContextStore`)
for scheduler services (for example generation tracking). That layer is not the
same as **lexical, subtree-local** values.

Without hierarchical overrides, local concerns (theme, locale, form scope,
library-specific policy) force **prop drilling** or ad hoc parameters through
components that do not care.

### 1.2 What the new surface does

- **`with app_context_override[K1, K2, ...](v1, v2, ...):`** installs a
  **structural** provider for a **fixed tuple of keys** at this slot. Keys are
  chosen at compile time (static subscript); values are normal reactive inputs to
  the guarded `with` body.
- **`use_app_context(key)`** resolves the **effective** value for that
  `AppContextKey` from the current **authored** lexical view, returns an
  **`ExternalStoreRef`** (same broad binding model as `use_grip`), and
  **rebinds** when the requested key or effective provider stream changes.
- **Authored hierarchical root is empty:** if nobody provided a key in the
  ancestor chain, reads fail deterministically (`LookupError`), rather than
  silently using a factory default from the key object for authored scope.
- **`None` as a provided value** means **transparent fall-through** for that key
  at that override: the parent chain supplies the effective value, and
  notifications can propagate through that proxy behavior.

### 1.3 What it is not

- Not a full DI container; not a replacement for explicit parameters when those
  are clearer.
- **Mount resolution does not read authored app context** (per design plan).
- Root **`get_app_context` / `has_app_context`** remain the internal store;
  **`get_authored_app_context` / `has_authored_app_context` / `use_app_context`**
  are the **authored** tree.

User docs should keep this split visible so bootstrap and library code do not
conflate the two stores.

---

## 2. Where to add documentation

### 2.1 Design doc refresh (`docs/design/`)

| Target | Action |
|--------|--------|
| [`docs/design/App_Context_Framework.md`](../docs/design/App_Context_Framework.md) | **Rewrite** from “current implementation” to a **two-layer model**: (1) root `AppContextStore` + `get_app_context` for internal/runtime services; (2) **authored** hierarchical lookup + `open_app_context_override` + `use_app_context` / `authored_app_context_ref`. Remove or retitle the “Known limitations — no nested override” section; replace with a short **architecture** subsection (lexical inheritance, component child contexts, `Drip` per key for selective notification). Link to `dev-docs/HierarchicalContextManagement.md` for full design history. Update **Primary tests** list (see §4). |

### 2.2 User docs (`docs/user/`)

| Target | Action |
|--------|--------|
| **New (recommended):** `docs/user/App_Context_And_Overrides.md` | **Create** as the main author guide: declare `AppContextKey` (identity, optional `factory`/`close` for **internal** store only—clarify authored emptiness), provider syntax and **static key** rules (mirror compiler diagnostics: `NAME`, `module.NAME`, `Class.NAME`; no calls/lambdas in `[]`), positional value arity, nesting, `None` fall-through, **`use_app_context` returns `ExternalStoreRef`** and pairs with normal ref usage patterns. One minimal end-to-end `@pyrolyze` example; optional second example for multi-key provider. |
| [`docs/user/Hooks_And_State.md`](../docs/user/Hooks_And_State.md) | **Add** `use_app_context` to the hook list and a short section: reactive read of authored context, `AppContextKey` argument, analogy to `use_grip`, link to `App_Context_And_Overrides.md`. |
| [`docs/user/Authoring_Overview.md`](../docs/user/Authoring_Overview.md) | **Optional** one paragraph + link under structural / scope topics. |
| [`docs/user/README.md`](../docs/user/README.md) | **Add** reading-order entry for the new app-context page if the README lists topics sequentially. |

### 2.3 Reference (`docs/reference/`)

| Target | Action |
|--------|--------|
| [`docs/reference/Public_API_Surface.md`](../docs/reference/Public_API_Surface.md) | **Add** `app_context_override` (special `with` form; not a normal function) and **`use_app_context`** under source-facing API; note `use_app_context` is implemented in `hooks.py` and re-exported from `pyrolyze.api`. |
| [`docs/reference/Glossary.md`](../docs/reference/Glossary.md) | **Add** short entries: *authored app context*, *app context override*, *transparent override* (`None` fall-through), *internal app context store* (optional disambiguation). |

### 2.4 Contributor / compiler (`docs/contributor/`)

| Target | Action |
|--------|--------|
| [`docs/contributor/Testing_And_Goldens.md`](../docs/contributor/Testing_And_Goldens.md) or AST doc | **Add a subsection** pointing to goldens / phase files for `app_context_override` lowering (for example `tests/data/v3_14/goldens/phase4_app_context_override.py`) and to `rewrite.py` helpers. |
| **Optional:** `docs/contributor/App_Context_Override_Lowering.md` | **Only if** maintainers want a dedicated page: guard shape (`visit_slot_and_dirty`, dirty fields for provider args), `open_app_context_override` call pattern, invalid forms. Otherwise a dev-docs pointer to `HierarchicalContextManagementPlan.md` phase 1 is enough. |

### 2.5 Runtime internals (dev-docs only)

Keep **`runtime/drip.py`** and override slot machinery documented primarily in:

- [`HierarchicalContextManagementPlan.md`](HierarchicalContextManagementPlan.md) (phase 3–4)

Optional short **“Implementation notes”** subsection in
`docs/design/App_Context_Framework.md` linking to `drip.py` and
`open_app_context_override` in `context.py`—avoid duplicating the plan doc.

---

## 3. How it works (outline for writers; verified against tests)

When drafting user-facing text, use this structure; trim jargon in `docs/user/`.

### 3.1 Compiler surface

- `with app_context_override[Ks...](*values):` lowers to a guarded
  `open_app_context_override(slot, keys_tuple, *values)` context manager on
  `RenderContext` / pass scope (see golden
  `tests/data/v3_14/goldens/phase4_app_context_override.py`).
- Static key validation and diagnostics: `rewrite.py` (`_app_context_override_key_exprs`, …).

### 3.2 Runtime: authored lookup chain

- Lexical nesting of `open_app_context_override` builds an overlay lookup;
  component child contexts inherit the effective authored view
  (`test_app_context_override_context.py`:
  `test_component_child_context_inherits_authored_override`).
- Root authored view is empty (`test_authored_app_context_root_is_empty`).
- Provider does not emit wrapper UI (`test_open_app_context_override_is_lexical_and_does_not_emit_wrapper_ui`).

### 3.3 `None` and notification semantics

- `None` value = fall-through for that key at that level
  (`test_none_override_falls_through_to_parent_value`).
- Per-key refs notify only when that key’s effective value changes
  (`test_authored_app_context_ref_notifies_only_changed_key`).
- Transparent (`None`) overrides forward parent updates; concrete inner values
  block outer notifications (tests
  `test_none_override_forwards_parent_notifications_through_proxy_drip`,
  `test_concrete_override_blocks_parent_notifications`,
  `test_transparent_override_unsubscribes_*`).

### 3.4 Internal store vs authored

- `AppContextStore` at root remains available for internal keys; authored
  overrides do not replace it
  (`test_internal_app_context_store_remains_separate_from_authored_overrides`).

### 3.5 Structural invariants

- Value arity must match key tuple arity
  (`test_open_app_context_override_validates_value_arity`).
- Fixed key tuple at a given slot cannot change across rerenders
  (`test_open_app_context_override_rejects_key_tuple_changes_at_same_slot`).

### 3.6 `use_app_context`

- Implemented in [`hooks.py`](../src/pyrolyze/hooks.py): requires plain-call
  context; returns `authored_app_context_ref(key)`.
- Tests: [`tests/test_use_app_context_runtime.py`](../tests/test_use_app_context_runtime.py)
  (read override, `LookupError` without provider, `TypeError` for non-key,
  rebind when requested key changes, read through `None` override with
  invalidation).

---

## 4. Test index (for doc authors and reviewers)

| Area | Tests |
|------|--------|
| Authored overrides, inheritance, `None`, refs, separation from store | `tests/test_app_context_override_context.py` |
| `use_app_context` hook + rebind | `tests/test_use_app_context_runtime.py` |
| Lowered source shape | `tests/data/v3_14/goldens/phase4_app_context_override.py` (+ any additional phase goldens / AST tests naming `app_context_override`) |
| Legacy / root store framework | `tests/test_app_context_framework.py` (still relevant for internal store docs) |

Grep for `app_context_override` and `use_app_context` under `tests/` when
finalizing to catch new files.

---

## 5. Suggested writing order

1. Update **`docs/design/App_Context_Framework.md`** so the design doc matches
   reality (stops claiming “no nested overrides”).
2. Add **`Public_API_Surface.md`** entries and **glossary** entries.
3. Add **`docs/user/App_Context_And_Overrides.md`** and link from
   **`Hooks_And_State.md`**.
4. Contributor golden/lowering pointer (small edit to existing contributor doc).
5. README / authoring cross-links as needed.

---

## 6. Non-goals

- Documenting GRIP-specific wrappers (belongs in grip repos) beyond “libraries
  can wrap `AppContextKey` + overrides”.
- Teaching `Drip` as a public API; keep it contributor/design-level.
- Replacing `HierarchicalContextManagement.md`; user docs should **link** to it
  for motivation and edge cases.
