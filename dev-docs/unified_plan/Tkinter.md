# Tkinter — unified adapter implementation plan

## Analysis status

Done or in progress:

- `UiInterface` / `kind` inventory: `dev-docs/widget-reconcile/widget_catalog_extract.json`
  (`tkinter.entries`, 105 kinds).
- Initial role triage: `dev-docs/widget-reconcile/RoleMatrix.md` (Tk column).

Still to analyse (before locking adapter signatures):

- **Classic vs ttk vs tix:** for each wave-1 role, pick the **default** kind
  (`ttk_*` preferred for parity with Qt/DPG styling hooks); document tix-only
  rows as toolkit-only.
- **Mount surface:** Tk mount selectors and mountable engine behavior for
  multi-pane examples (grid/pack semantics vs Qt layout).
- **Option database / ttk.Style:** how theme tokens from app context map to
  `TK_CONFIG` / style configuration (best-effort matrix).

## Deliverables (this backend)

- Concrete **adapter class** (unified base subclass); **same method names** as Qt
  and DPG; delegates to `TkinterUiLibrary` where needed.
- Reference layout or test proving canonical mount keys for a Tk root +
  `Toplevel` if multi-window is in wave 1.
- `RoleMatrix.md` updates for Tk-specific **best-effort** caveats.

## Implementation checklist

- [ ] Confirm package location and public import path.
- [ ] Wave 1: unified symbols with `ttk` defaults where possible.
- [ ] Mount key mapping documented.
- [ ] App context: map tokens to ttk.Style / widget config where feasible.
- [ ] Tests: headless-friendly skips documented for CI if needed.
- [ ] Cutover: no `backends/common/` for Tk examples (Phase 5).

## Open questions

- **Float / geometry:** unified `window_shell` vs `ReactiveRootWindowProxy.md`
  for `Toplevel` lifetime.
- **Date/time** widgets — likely toolkit-only or very narrow unified surface.
