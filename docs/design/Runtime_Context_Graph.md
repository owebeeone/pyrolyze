# Runtime Context Graph

## Purpose

Explain the runtime's context graph, slot ownership, structural ownership, and
committed UI behavior.

## Current implementation

The runtime core lives in `src/pyrolyze/runtime/context.py`.

The main object is `RenderContext`. It owns:

- slot creation and lookup
- pass/commit/rollback boundaries
- invalidation scheduling
- post-commit callbacks
- committed UI
- app-context access

Important runtime context kinds include:

- `RenderContext`
- `PlainCallSlotContext`
- `ContainerSlotContext`
- `ComponentCallSlotContext`
- `KeyedLoopSlotContext`
- `LoopItemSlotContext`
- `LeafSlotContext`
- `EventHandlerSlotContext`

The runtime distinguishes:

- structural ownership
  - who owns child contexts and slots
  - who decides visitation and teardown
- render ownership
  - who receives emitted UI at commit time

Committed UI is tracked per context and propagated upward after successful
commits. This is what backend reconcilers consume.

## Code map

- runtime core
  - `src/pyrolyze/runtime/context.py`
- app-scoped values
  - `src/pyrolyze/runtime/app_context.py`
- graph capture helpers
  - `src/pyrolyze/visitor.py`

## Primary tests

- `tests/test_context_graph_phase1.py`
- `tests/test_context_graph_phase3_phase4.py`
- `tests/test_context_graph_phase5_component_call.py`
- `tests/test_context_graph_phase5a_invalidation_kernel.py`
- `tests/test_context_graph_phase6_use_effect.py`
- `tests/test_context_graph_phase7_native_ui.py`
- `tests/test_context_graph_phase8_scheduler.py`
- `tests/test_visitor_context_graph.py`
- `tests/test_visitor_context_graph_integrated.py`

## Known limitations

- some higher-level source features still rely on the runtime being more mature than compiler lowering
- async-effect tracing is still more limited than synchronous effect tracing

## Future proposals

- broader runtime introspection APIs
- richer graph diffs and lifecycle tracing
- tighter source/runtime alignment for more advanced event and hook patterns
