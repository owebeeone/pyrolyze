# Hooks And State

The current public hooks live in `src/pyrolyze/hooks.py` and are re-exported
through `pyrolyze.api`.

Current hook surface:

- `use_state`
- `use_effect`
- `use_mount`
- `use_unmount`
- `use_grip`

## `use_state`

`use_state(initial)` returns:

- current value
- setter

The setter accepts either:

- a direct replacement value
- an updater function

## `use_effect`

`use_effect(effect, deps=...)` stages an effect request handled by the runtime.

Current behavior:

- first committed run schedules the effect
- dependency changes reschedule it
- deactivation runs cleanup

## `use_mount` and `use_unmount`

Convenience forms built on the same effect machinery.

## `use_grip`

`use_grip(...)` expects an external-store reference or an object that exposes
`ref()`.

The runtime subscribes to that store and queues invalidation when the source
changes.

## Testing hooks

Good test layers:

- direct runtime tests for hook behavior
- compiled source-backed tests for lowering behavior
- integrated context-graph tests for rerender isolation

See [Testing_Pyrolyze_Code.md](Testing_Pyrolyze_Code.md).
