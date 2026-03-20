# Studio Parity Checklist

Source baseline:
- [Studio App Spec Baseline.md](C:/Users/adria/Documents/Projects/py-rolyze-wip/Studio/Studio%20App%20Spec%20Baseline.md)
- [examples/studio_app.py](C:/Users/adria/Documents/Projects/py-rolyze-wip/examples/studio_app.py)

## Execution Rules

- TDD-first for each parity slice (red/green/refactor).
- Keep baseline placeholders explicit unless intentionally upgraded.
- Record each implemented interaction against baseline IDs (`I-001` .. `I-072`).

## Phase Status

| Phase | Scope | Status |
|---|---|---|
| Phase 0 | Parity map + contracts + custom-node scaffolding | In progress |
| Phase 1 | Window shell/chrome parity | In progress |
| Phase 2 | Workspace layout (splitters/tabs/panels) parity | In progress |
| Phase 3 | Explorer + menu/status command parity | Not started |
| Phase 4 | Inspector parity (hierarchy/highlight/screenshot/draw/save) | Not started |
| Phase 5 | Persistence + startup/shutdown parity | Not started |
| Phase 6 | Performance guardrails + final parity report | Not started |

## Custom Studio Node Contract (Initial)

Studio-specific custom kinds introduced for parity migration:

- `studio_splitter`
- `studio_tabs`
- `studio_tab_page`
- `studio_toolbar`
- `studio_tree_view`
- `studio_status_strip`
- `studio_overlay_canvas`
- `studio_screenshot_canvas`

These are currently Studio-local and may be promoted into shared Pyrolyze standards later.

## Baseline Interaction Group Tracking

| Group | Baseline Sections / IDs | Target | Status |
|---|---|---|---|
| Startup/CLI | 5.1, `I-001..I-006` | Match startup semantics | In progress |
| Shell + Context menu | 5.2-5.5, `I-007..I-025` | Frameless parity with move/resize/context behavior | In progress |
| Menus + shortcuts | 5.6-5.8, `I-026..I-042` | Match menu wiring and shortcut behavior | Not started |
| Explorer + tabs/panel | 5.9-5.10, `I-043..I-052` | Real tree + tab interactions | In progress |
| Status bar | 5.11, `I-053` | Match status strip structure and updates | Not started |
| Inspector core | 5.12, `I-054..I-061` | Hierarchy + hover/sticky highlight | Not started |
| Inspector screenshot | 5.13, `I-062..I-068` | Capture + draw + save parity | Not started |
| Persistence + async | 5.14-5.15, `I-069..I-072` | Restore/save + async boundary parity | Not started |
