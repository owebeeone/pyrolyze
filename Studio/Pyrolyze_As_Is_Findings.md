# PyRolyze As-Is Findings (Studio Prototype)

Date: `2026-03-20`

This note summarizes what was achievable for Studio with current PyRolyze capabilities,
using the prototype in:

- [studio_poc.py](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/studio_poc.py)
- [run_studio_poc.py](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/run_studio_poc.py)

## What Works Today

- Stateful UI with `use_state(...)` and event handlers.
- Dynamic list rendering with `keyed(...)`.
- Basic composition using current semantic kinds:
  - `section`
  - `row`
  - `badge`
  - `button`
  - `text_field`
  - `toggle`
  - `select_field`
- Readable “Studio-like” prototype with:
  - explorer simulation
  - editor preview simulation
  - bottom panel mode switching
  - inspector snapshot simulation

## Key Gaps Observed

- No native `splitter` semantic node.
  - Cannot model real resizable multi-pane workspace declaratively.
- No native `tabs`/`tab_page` nodes.
  - Editor and panel tabs must be simulated rather than true tab widgets.
- No model-backed tree node contract.
  - Real `QTreeView + QFileSystemModel` behavior requires custom bridge work.
- No built-in rich text area/editor node.
  - Large text content is pushed through `badge`/`text_field` workarounds.
- Host-shell integration is ad hoc.
  - Requires explicit glue for menu/status/title-bar action pathways.
- Advanced custom widget lifecycle is not first-class.
  - Inspector overlay/screenshot drawing need explicit bridge ownership rules.

## Priority Improvements for Studio

1. Add semantic node kinds: `splitter`, `tabs`, `tab_page`, `tree_view`, `text_area`.
2. Add model-backed tree binding contract with stable row identity.
3. Formalize host mount-point/action bridge API.
4. Add supported custom-widget bridge lifecycle (create/update/dispose).
5. Add performance regression guards for reorder-heavy and large-tree reconciliation.

