# Reactive Root and Window Proxy

## Purpose

This document proposes a **root-level reactive model** for PyRolyze apps that
need to **create, show, hide, and retire multiple windows** (or window-like
surfaces) from reactive state. It complements:

- `dev-docs/UnifiedMountBasedNativeApi.md` — mount-first unified surface and
  adapters.
- `dev-docs/WidgetReconcilePlan.md` — phased inventory, adapters, and cutover.

The core issue: **native windows are not ordinary widget nodes.** In Qt, Tk, and
Dear PyGui, a top-level window has **toolkit-owned lifetime**—the user can
close it, the platform can destroy it, and event loops may deliver teardown
asynchronously. If the reactive tree treated a window like an inner `UIElement`
with only reconcile identity, authors would see **dangling references**, **state
forks**, and **impossible** “reopen the same logical window” semantics.

The proposal: introduce a **window proxy** (stable logical handle) that sits
between reactive state and the **native window handle**. Reconciliation maps
proxy ↔ native window and explicitly models **attach, detach, user-close, and
explicit dispose**.


## Problem

- **Lifetime mismatch:** Reactive components assume tree-driven mount/unmount;
  windows often outlive or die independently of a parent slot’s next render.
- **Identity:** Authors need a **stable id** for “this document window” or
  “that tool palette” across rerenders, even if the native widget was recreated.
- **Multi-window apps:** A single root reconcile pass that only fills one
  `QMainWindow` or one DPG viewport is not enough; the **set of windows** must
  be data-driven.
- **Cross-cutting policy:** Theme and density (via app context) should apply per
  window or per window class; the proxy is a natural scope boundary for
  overrides without entangling mount resolution.


## Goals

- **Reactive window set:** Root (or dedicated host) reads reactive state and
  decides **which window proxies should exist** and with what props (title,
  modality hints, initial geometry where portable).
- **Stable proxy identity:** One logical window = one proxy id across the
  session unless the author explicitly creates a new logical window.
- **Explicit native binding:** Runtime maintains `proxy → native_window` with
  clear transitions: created, shown, hidden, **native destroyed** (user close),
  **proxy retired** (author removed from reactive set).
- **Toolkit parity at the semantic level:** Same **names** and **state machine**
  on the unified/proxy API; native hooks differ per backend behind adapters.
- **Composable with mounts:** Content *inside* a window still uses
  `advertise_mount` / `mount` and the unified widget adapters; the proxy owns
  the **shell**, not every leaf.


## Non-Goals

- A single abstraction that hides all platform window manager quirks (full-screen
  spaces, macOS sheets, etc.) in v1; document **best-effort** vs **toolkit-only**
  in the same spirit as the widget reconcile matrix.
- Replacing the main event loop or process model.
- GRIP wire format for windows (sibling repos may mirror proxy ids; out of
  scope here).


## Concepts

### Root (reactive host)

The **root** is the reactive site that owns **window policy**: which proxies
exist, their ordering or z-order hints, and default app-context overrides for
subtrees hosted inside each window. It may be:

- a top-level `@pyrolyze` component run by the app bootstrap, or
- a small imperative host API that feeds the same reconcile pipeline from
  non-tree code (exact shape is an implementation choice).

The important part: **window set is derived from reactive inputs**, not only from
one-shot imperative `show()`.

### Window proxy

A **window proxy** is a small **logical object** (id + metadata + content
factory or slot reference) that:

1. **Survives** native teardown: if the user closes the window, the proxy may
   enter a `closed` / `detached` state while reactive state catches up, or be
   removed on the next frame—policy must be **one documented behavior**, not
   three accidental ones per toolkit.
2. **Rebinds:** if the same logical window is shown again, the runtime may
   allocate a **new** native window while preserving **proxy id** and author
   state.
3. **Scopes context:** optional `app_context_override` applied at the proxy
   boundary so inner content sees per-window theme without global mutation.

The proxy is **not** the native `QWindow` / `Toplevel` / DPG window id; it is
the PyRolyze-side handle authors and state refer to.

### Native window handle

Toolkit object with **independent lifetime**. Adapters subscribe to **close**
and **destroy** signals to update proxy state and prevent reconcile from assuming
the handle is still valid.


## State machine (author-facing)

Exact enum names are TBD; the **required transitions** are:

| Transition | Meaning |
| --- | --- |
| `requested` | Reactive root wants this window to exist. |
| `native_attached` | Proxy bound to a live native window; content reconciling inside. |
| `hidden` | Logical window retained but not shown (if toolkit supports without destroy). |
| `native_closed` | User or OS closed native window; proxy notified. |
| `retired` | Author removed window from reactive set; native dispose if still alive. |

Rules to design explicitly:

- Whether `native_closed` **auto-removes** the proxy from author state or **keeps**
  it until the next reactive commit (recommended: **event callback** or
  `use_effect`-style hook so authors choose).
- Whether recreating the same proxy id after `retired` is allowed (usually yes,
  as a new cycle).


## Relationship to unified mount API

- **Proxy** = shell and lifetime; **mounts** = interior layout regions.
- A window’s content root should still **advertise** canonical mount keys
  (`shell.body`, `shell.chrome`, … — see `dev-docs/MountKeys.md` and
  `dev-docs/ReferenceShellLayout.md`) inside that window’s reconcile scope.
- Widget adapters read **app context** inside the window subtree; they do not
  resolve mounts from context (unchanged rule from hierarchical context plan).


## Implementation sketch (phased)

1. **Per-toolkit adapter hooks:** map proxy operations to `QMainWindow` /
   `QDialog` / `Toplevel` / DPG window APIs; unify **operation names** across
   three adapter modules (same rule as widget reconcile).
2. **Runtime registry:** weak or strong maps `proxy_id → NativeWindowBinding`;
   invalidate on native destroy.
3. **Tests:** simulate user-close and assert proxy state + no double-free;
   reactive add/remove of window from a list drives attach/retire.
4. **Docs + one example** per toolkit showing two windows driven from state.

## Open Questions

- Single global root vs **nested** proxy (e.g. dialog owned by document window).
- Modality and transient-parent behavior on each toolkit.
- Whether proxy ids are **author-supplied** strings, **compiler-stable** keys, or
  opaque runtime ids.
- Interaction with GRIP: whether proxy id is the stable cross-process handle
  later.


## Acceptance criteria (for a future implementation phase)

When this proposal is implemented, the following should hold:

- [ ] **Documented state machine** and one chosen policy for user-close vs
      reactive removal.
- [ ] **Three backends** (or documented skip) implement the same named proxy
      operations on the adapter surface.
- [ ] **Tests** cover: open two windows from state; close one natively; remove
      one from state; assert registry and reconcile stay consistent.
- [ ] **Example** (or test-backed demo) showing reactive window list + inner
      `advertise_mount` layout.
- [ ] **App context** can be scoped per proxy subtree in at least one toolkit
      without affecting siblings.

## Cross-References

- `dev-docs/ReferenceShellLayout.md` (canonical shell tree + per-backend selectors)
- `dev-docs/MountKeys.md` (key constants table)
- `dev-docs/UnifiedMountBasedNativeApi.md`
- `dev-docs/WidgetReconcilePlan.md` (deliverables table links here)
- `dev-docs/HierarchicalContextManagementPlan.md` (context boundaries)
