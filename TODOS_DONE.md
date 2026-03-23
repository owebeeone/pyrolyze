# Completed TODOs

Completed backlog items moved out of [TODOS.md](TODOS.md) to keep the active list focused.

## Milestone: Initial Release (PyPI)

### Release Blockers

- [P1] Fix callable-annotation cache writes for non-attribute callables (for example builtins). Resolved on 2026-03-20.
  - Implemented safe callable cache read/write fallback when direct `setattr(...)` is unsupported.
  - Added signature-introspection fallback for `inspect.signature(...)` `TypeError`/`ValueError` paths.
  - Covered by regression tests for `call_plain(...)`, `leaf_call(...)`, and `container_call(...)`.

- [P1] Fix `AppContextStore` cache miss detection for `None` values. Resolved on 2026-03-20.
  - `AppContextStore.get(...)` now uses an explicit sentinel for cache misses, so `None` is a valid cached value.
  - Factories returning `None` are no longer re-run on repeated access.
  - Close-callback order entries no longer duplicate when cached values are `None`.

- [P1] Implement compiler-generated `call_site_id` emission for every lexical UI emission site. Resolved on 2026-03-20.
  - The v3.14 compiler now stamps lowered `call_native(...)` emissions with `__pyr_call_site_id`.
  - Runtime native emission metadata now carries both `call_site_id` and slot identity/slot-path lineage for instance disambiguation.
  - UI normalization/reconciliation now consumes this metadata for deterministic, stable node identity.

### Strongly Recommended Before Release

- [P2] Invalidate transformer-fingerprint hash cache when compiler files change in-process. Resolved on 2026-03-20.
  - `active_transformer_fingerprint(...)` now derives a source-state token from fingerprint-file metadata and keys transform-hash caching by `(version, source_state_token)`.
  - In-process compiler/kernel edits and file add/remove now force transform-hash recomputation without manual cache clears.
  - Added explicit `invalidate_transformer_fingerprint_cache()` and regression tests for edit detection, file-set changes, and unchanged-state cache hits.

- [P2] Remove quadratic replacement-path work in `reconcile_owner(...)`. Resolved on 2026-03-20.
  - Replaced replacement tracking list scans with set-based membership (`id(old) in replaced_node_ids`) in the detach pass.
  - This removes the replacement-heavy O(n^2) detach predicate path.
  - Added reconciliation regression coverage for replacement-heavy updates and detach/dispose behavior.

- [P2] Reduce quadratic child placement work in reconciliation/backends. Resolved on 2026-03-20.
  - Reconciliation now uses minimal placement planning and skips unchanged `place_child(...)` operations.
  - PySide6 layout placement now tracks widget order/index with cached state plus resync fallback, reducing repeated `_layout_index(...)` scans.
  - Tkinter pack placement now tracks packed order/index and avoids repeated `pack_slaves()` scans in hot placement paths.

### Can Defer Until After Initial Release

- [P3] Add explicit backend-swap handling in owner reconciliation. Resolved on 2026-03-20.
  - `UiOwnerCommitState` now tracks `last_backend_identity` and `reconcile_owner(...)` computes semantic backend identity (`type + backend_id`).
  - On backend identity change, reconciliation now performs a full owner clear/remount rather than attempting incremental reuse.
  - Added tests covering swap-remount behavior and non-remount behavior for same-identity backend instances.

## Milestone: Studio App Enablement (PyRolyze + PySide6)

### Development Prerequisites (Must-Have)

- [P1] Define and adopt a standard `UIElement` component helper surface for app code. Resolved on 2026-03-20.
  - Added canonical helper component refs in `src/pyrolyze/ui/elements.py` and re-exported via `pyrolyze.ui`.
  - Refactored `examples/grid_app.py` and `Studio/ui/studio_root.py` to consume the shared helper surface.
  - Replaced duplicated Studio helper definitions with a compatibility re-export module and added focused helper-surface regression tests.
