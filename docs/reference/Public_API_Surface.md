# Public API Surface

## Source-facing API

Defined in `src/pyrolyze/api.py`:

- `pyrolyze`
- `reactive_component`
- `pyrolyze_slotted`
- `pyrolyze_component_ref`
- `call_native`
- `keyed`
- `UIElement`
- `ComponentMetadata`
- `ComponentRef[...]`
- `PyrolyteHandler[...]`
- `SlotCallable[...]`
- `CallFromNonPyrolyzeContext`

Hooks re-exported from `src/pyrolyze/hooks.py`:

- `use_state`
- `use_effect`
- `use_mount`
- `use_unmount`
- `use_grip`

## Compiler-facing public API

Defined in `src/pyrolyze/compiler/__init__.py`:

- `analyze_source`
- `lower_plan_to_ast`
- `emit_transformed_source`
- `build_debug_artifacts_for_source`
- `load_transformed_namespace`
- `compile_source`
- `compile_source_with_env`
- `write_debug_artifacts`
- `kernel_loader`

## Runtime-facing public API

Defined in `src/pyrolyze/runtime/__init__.py`:

- `RenderContext`
- `dirtyof`
- `PlainCallRuntimeContext`
- `ExternalStoreRef`
- `UseEffectRequest`
- `UseEffectAsyncRequest`
- `AppContextKey`
- `AppContextStore`
- `GenerationTracker`
- `TraceChannel`
- `configure_trace`
- reconciler primitives from `ui_nodes.py`
