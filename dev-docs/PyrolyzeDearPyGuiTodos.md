# DearPyGui / DPG integration — backlog (verified against repo)

External review described an OOP “`ContainerNode` + manual `tag=` + `unmount()` leaves `parent.children`” wrapper. **That code is not in this repository** (no matches for `ContainerNode`, `_mark_unmounted_recursive`, or `Update Error` in `py-rolyze/src`).

The **AI-proposed reference implementation** that motivated much of that review is archived verbatim in [`DearPyGuiAiRecommendedOopWrapper.md`](DearPyGuiAiRecommendedOopWrapper.md) (not shipped as library code).

Items below record **what applies to PyRolyze today** (`MountableEngine`, `LiveDpgHost`, `DpgMountableEngine`, `UIElement` / `DearPyGuiUiLibrary.C`, examples) and **what to harden**.

| # | Claim | Verified in this repo? | Notes / location | TODO |
|---|--------|-------------------------|------------------|------|
| 1 | **Zombie nodes**: `unmount()` clears DPG but leaves objects in `parent.children` → unbounded Python growth | **Not applicable as stated** | Core path uses `MountedMountableNode` + `_dispose_node_subtree` when children drop out of reconciliation (`mountable_engine.py`). No persistent OOP child list like the review. | **Doc / guardrails**: If we ship or endorse any tutorial “mutable Python tree + manual unmount”, require explicit removal from parent lists or forbid that pattern. Add a short note in DPG dev-docs pointing authors at `UIElement` rebuild + mount engine instead. |
| 2 | **Tag / ID collision**: user-supplied string tags collide across list re-renders | **Partially applies** | `UIElement.slot_id` + `LiveDpgHost.allocate_tag(slot_id)` reuse the same DPG tag for the same slot (`live_host.py`). Duplicate `slot_id` in one tree → collision / wrong reuse. Compiler/keyed paths generate identities; **hand-written** trees (e.g. `examples/dearpygui_demo_trees.py`) use string `slot_id=` patterns that must stay unique per instance. | **Product**: Optional lint or debug assert for duplicate `slot_id` in a committed tree; document “slot_id = stable identity, must be unique”. Consider generated prefixes for author-facing helpers where feasible. |
| 3 | **Table trap**: rows before columns → DPG errors | **Gap (partially addressed)** | Specs already split `column` vs `row` mount points (`generated_library.py`); authors could still mis-order flat `children`. | See **§ Stashed: table API layering** below. Remaining: runtime validation of kinds/counts, docs, optional migration of examples to `TableOrdered`. |
| 4 | **Child order never updates** (append-only mount) | **Mostly mitigated for native path** | `backends/mounts.py` implements ordered reconciliation (`incremental_ordered_replay`, `place_child`, etc.). `DpgContainerItem.sync_children` (`items.py`) reparents with `move_item(..., before=0)` in a loop—worth confirming this always matches **declared** child order for every mount plan. | **Audit**: Trace `direct_sync` → `sync_children` for multi-child DPG containers vs `place_child` index path; add regression tests if order can diverge. |
| 5 | **`except Exception: print(...)` in hot update path** | **Not found in PyRolyze src** | No `Update Error` / similar flood pattern under `py-rolyze/src`. | **Policy**: If adding defensive logging around DPG configure/update, use throttled logger + counter, not unbounded `print` in tight loops. |
| 6 | **`InputText` hardcodes `on_enter=True`** | **Not verified** | Generated `DpgInputText` params default `on_enter` to `False` (`generated_library.py` `UiParamSpec` / props). `author_ui.DearPyGuiC.InputText` does not force `on_enter`. | **Watch**: Any future high-level wrapper that sets `on_enter=True` by default should expose it as an explicit opt-in. |
| 7 | **Tight `while dpg.is_dearpygui_running()` burns CPU** | **Not as stated** | Native host uses `dpg.start_dearpygui()` (`pyrolyze_native_dearpygui.py`). `LiveDpgHost` exposes `vsync` (default `False`)—authors may want vsync or DPG `configure_app` fps for laptop-friendly behavior. | **Docs / defaults**: Mention viewport vsync / fps in runner examples; consider documenting recommended `vsync=True` for idle-friendly demos. |

## Stashed: table API layering (columns before rows)

**Goal:** Make it awkward or impossible (at the Python API shape level) to call “rows” before “columns” when building author-facing `UIElement` trees.

**Implemented (optional path):**

- `pyrolyze.backends.dearpygui.author_ui`: `DearPyGuiC.TableOrdered(...)` → `DearPyGuiTableColumnPhase.columns(*cols)` → `DearPyGuiTableRowPhase.rows(*rows)` → `UIElement` with `children=columns + rows`.
- Types `DearPyGuiTableColumnPhase` / `DearPyGuiTableRowPhase` expose only the next legal step (no `.rows` on the column phase, no `.columns` on the row phase).
- Tests: `tests/test_dearpygui_table_ordered_author_ui.py`.

**Not replaced:** `DearPyGuiC.Table(children=...)` remains for full control; wrong order is still possible there.

**Follow-ups if we push this further:** document in DPG authoring notes; use `TableOrdered` in one example; add optional `.rows()` checks (e.g. non-empty columns); consider mount-engine assert on `DpgTable` child sequence for debug builds.

## Summary

- The review is a good checklist for **ad-hoc DPG OOP wrappers**; **PyRolyze’s mountable pipeline already addresses disposal and (mostly) ordered reconciliation**—but **slot_id discipline**, **table structure**, and **sync vs place ordering** still deserve work.
- Items **1, 5, 6, 7** are largely **external or N/A** to current `src`; kept as **process / future-code** TODOs so new code does not reintroduce them.
