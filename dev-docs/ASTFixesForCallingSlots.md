# AST Fixes For Calling Slots

## Problem

Slot-bearing calls such as `use_grip(...)`, `use_state(...)`, and related slotted helpers do not fit naturally into ordinary Python expressions under the current lowering model.

Today, the compiler effectively treats a slot-bearing call as if it returns:

- the logical value
- hidden dirtiness information

That makes simple code like:

```python
value = use_grip(STORE) or "clock"
count = int(use_grip(STORE) or 0)
```

awkward to lower, because the surrounding expression only expects one value, while the compiler/runtime currently want more than one channel.

## Scope

### Phase 1

Phase 1 should:

- replace the old `plain_call` model for slot-bearing expressions
- introduce a new `slot_expr` model
- continue to disallow slot-bearing comprehensions
- continue to require keyed `for` loops for slot-bearing repeated structure

That means:

- slot-bearing ordinary expressions are in scope
- slot-bearing comprehensions are out of scope

Examples explicitly out of scope for Phase 1:

```python
[use_grip(k) for k in keyed(keys, key=lambda k: k)]
{k: use_grip(k) for k in keyed(keys, key=lambda k: k)}
```

### Phase 2

After the `slot_expr` model exists, decide whether keyed comprehensions are worth implementing or should remain unsupported.

## Chosen Direction

The chosen direction is:

1. the old `plain_call` model is removed for slot-bearing expression lowering
2. slot-bearing expressions are lowered into an explicit `slot_expr`
3. a `slot_expr` contains one or more call sites to slotted functions
4. the source expression is rewritten into a lambda over per-call evaluators
5. dirtiness is managed by a runtime dirtiness manager that is updated during evaluation
6. a scoped dirtiness sink is attached explicitly with `apply_dirt_sink(...)`
7. final value binding and final dirty binding happen at a distinct `evaluate(...)` step

This is not a “dirty sink” model in the loose sense. The core abstraction is the slotted expression plus its call-site evaluators.

## Compiler-Inserted Names

This design must follow the existing compiler convention that AST-introduced names are prefixed with `__pyr_`.

The current compiler already uses `__pyr_*` for inserted names such as:

- `__pyr_ctx`
- `__pyr_slot_1`
- `__pyr_module_id`
- `__pyr_dirty_state`

So any new lowering-only helper names introduced by this design must also use that reserved prefix.

That includes concepts such as:

- slot context
- dirt manager
- slot-expression temporaries
- internal evaluator bindings

Examples of acceptable lowered-only names:

- `__pyr_slot_ctx`
- `__pyr_dm`
- `__pyr_slot_expr_1`
- `__pyr_eval_v1`

This avoids collisions with user-authored identifiers such as:

- `literal`
- `slot_ctx`
- `dirt_manager`

In design examples, human-readable names may still be shown without the prefix for clarity, but the lowered compiler form should treat all such helpers as `__pyr_*` internal names.

For this design specifically:

- the central dirt manager in lowered code should be `__pyr_dm`
- bound dirt writes should lower through `__pyr_dm.bind`
- initial-render/literal dirt should come from the existing slot-context surface
- call-site identity should use a compiler-generated `SlotId`, not only a temporary evaluator variable name

## Core Runtime Carriers

The parameter carrier for both value-side arguments and dirty-side arguments should be one normalized dataclass shape.

Conceptually:

```python
@dataclass(frozen=True, slots=True)
class Args[T = Any]:
    args: tuple[T, ...]
    kwds: dict[str, T]

    def call(self, func: Callable[..., Any]) -> Any:
        return func(*self.args, **self.kwds)

    @classmethod
    def capture(cls, *args, **kwds) -> "Args[T]":
        return cls(tuple(args), dict(kwds))
```

This means:

- `slot_params(...)` should produce `Args[Any]`
- `slot_params_dirt(...)` should produce `Args[bool]` or a structurally equivalent `Args` carrying dirty values in the same positional/keyword structure

The key rule is:

- the dirty-side carrier mirrors the value-side carrier exactly

This keeps binding, caching, and runtime invocation symmetric.

## Single-Call Fast Path

The design should explicitly allow a fast path for the common case where the entire expression is one slot-bearing call.

Example:

```python
value = use_grip(STORE)
```

This is not a reason to preserve `plain_call`.

Instead:

- the semantic model remains `slot_expr`
- the compiler may choose a simplified lowering shape for the single-call case
- the runtime may choose a specialized implementation that avoids unnecessary lambda or object overhead

The key rule is:

- fast-pathing is an optimization inside the new `slot_expr` model
- it is not a second runtime contract

So the design allows:

- one general `slot_expr` lowering for arbitrary expressions
- one specialized single-call lowering for the trivial case

as long as both:

- write through the same dirt manager
- use the same structural dirty-binding rules
- expose the same observable semantics

## Core Model

## Slot Expression

A slot-bearing expression is lowered into a runtime object conceptually like:

```python
slot_ctx.slot_expr(value_lambda, dirty_lambda)
```

The `slot_expr`:

- belongs to the current parent slot
- contains one or more slot-bearing call sites
- evaluates the expression using lazy, memoized per-call evaluator objects
- carries a dirtiness sink for final bound outputs
- binds final results only at the end
- should stage lifecycle updates and final dirty bindings until a successful pass commit

## Call Sites

Each slot-bearing call inside the expression becomes a call site inside that `slot_expr`.

Important:

- a call site is not a new child slot
- it is a call inside the current slot
- it still needs a stable per-expression call-site identity
- it is evaluated lazily only if the expression requests it

That identity should be a real compiler-generated call-site `SlotId`.

So conceptually:

- evaluator lambda names like `v1` are just rewrite conveniences
- the persistent runtime identity should be the full call-site `SlotId`
- `slot_call(...)` should ultimately carry that `SlotId`

So for:

```python
value = use_grip(STORE) or "clock"
```

there is:

- one parent slot
- one `slot_expr`
- one call site inside that `slot_expr`

For:

```python
total = use_grip(A) + use_grip(B)
```

there is:

- one parent slot
- one `slot_expr`
- two distinct call sites inside that `slot_expr`

## Value Lambda

The source expression is converted into a lambda over evaluator parameters.

Example:

```python
value = use_grip(STORE) or "clock"
```

conceptually becomes:

```python
slot_ctx.slot_expr(
    lambda v1: v1.eval() or "clock",
    ...
)
```

Then:

```python
.slot_call(
    call_slot_id_v1,
    use_grip,
    lambda: slot_params(STORE),
    lambda: slot_params_dirt(slot_ctx.literal(STORE).dirty),
)
```

registers the call site associated with the evaluator parameter `v1`.

The evaluator is unified:

- `v1.eval()` returns the logical value for that call site
- `v1.dirty()` returns the dirty result for that call site

The evaluator must be lazy and memoized:

- the call site is evaluated only the first time `eval()` or `dirty()` needs it
- later accesses reuse cached results
- Python control flow such as short-circuiting determines which call sites are actually evaluated

Memoization here should match `plain_call` semantics rather than merely skipping all work:

- if function identity, schema, and input values do not require reinvocation, the original function call may be skipped
- binding-specific refresh behavior must still run when applicable
- for example, an external-store-backed call may refresh from the store without reinvoking the original callable

This is essential. Call sites must not execute eagerly in registration order.

For the single-call fast path, the implementation may bypass parts of the general lambda-wrapper machinery internally, but it must preserve the same externally visible behavior as the general `slot_expr` model.

## Expression Transform

The compiler should lower a slot-bearing expression in two parallel forms:

- a value lambda
- a dirty lambda

Both are derived from the same source AST and share the same evaluator parameters.

Conceptually, for an expression `E`, the compiler constructs:

- `V(E)` = value transform
- `D(E)` = dirty transform

and lowers to:

```python
slot_ctx.slot_expr(
    lambda ...: V(E),
    lambda ...: D(E),
)
```

Then each slot-bearing call site extracted from `E` is attached with `slot_call(...)`.

## Slot-Call Extraction

When the compiler sees a slot-bearing call inside an expression, it should:

1. allocate a call-site id inside the current parent slot
2. replace that call node in the expression with an evaluator parameter
3. add a corresponding `.slot_call(...)` entry

Example source:

```python
use_grip(A) + use_grip(B)
```

becomes conceptually:

```python
slot_ctx
    .slot_expr(
        lambda a, b: a.eval() + b.eval(),
        lambda a, b: a.dirty() or b.dirty(),
    )
    .slot_call(call_slot_id_a, use_grip, lambda: slot_params(A), lambda: slot_params_dirt(dm.A))
    .slot_call(call_slot_id_b, use_grip, lambda: slot_params(B), lambda: slot_params_dirt(dm.B))
```

## Nested Extraction

This extraction applies recursively.

If a slot-bearing call appears inside another argument expression, the compiler should recursively split the AST until each slot-bearing call site becomes one evaluator parameter.

That means the compiler must maintain:

- the lambda being built
- the list of evaluator parameters it needs
- the `.slot_call(...)` definitions that back those evaluators

So nested slot-bearing calls are not a special separate system. They use the same recursive extraction rule.

## Dirty Lambda

The dirty lambda computes final result dirtiness for the expression.

However, dirtiness may depend on:

- dirty state of a call
- actual value of a call

because control flow can depend on values.

So the dirty lambda likely cannot be purely over dirty evaluators alone.

For the fallback example:

```python
value = use_grip(STORE) or "clock"
```

the final value depends on whether `use_grip(STORE)` is truthy.

So the dirty path may need access to the same evaluators used by the value path, not a separate evaluator family.

Conceptually:

```python
slot_ctx.slot_expr(
    lambda v1: v1.eval() or "clock",
    lambda v1: v1.dirty(),
)
```

The exact API can vary, but the important point is:

- dirty evaluation may depend on the value path
- the evaluator object may need value-aware dirty semantics internally

## Dirty Transform

Under the chosen lazy evaluator model, the dirty transform can be simpler than the value transform.

The key rule is:

- if a subexpression is not evaluated, its dirty result is clean/false

Because of that, short-circuit control flow is already captured by lazy evaluation of the evaluator itself.

So for many expressions, the dirty transform can be defined structurally.

### Base cases

Literal or constant:

```python
V(3) = 3
D(3) = slot_ctx.literal(3).dirty
```

Local name:

```python
V(x) = x
D(x) = dm.x
```

Slot-bearing call site replaced by evaluator:

```python
V(call_i) = vi.eval()
D(call_i) = vi.dirty()
```

### Structural cases

Tuple:

```python
V((a, b)) = (V(a), V(b))
D((a, b)) = (D(a), D(b))
```

List:

```python
V([a, b]) = [V(a), V(b)]
D([a, b]) = [D(a), D(b)]
```

Dict:

```python
V({"x": a}) = {"x": V(a)}
D({"x": a}) = {"x": D(a)}
```

### Operators

For pure operator-style expressions:

```python
V(a + b) = V(a) + V(b)
D(a + b) = D(a) or D(b)
```

The same rule works for many pure expression forms because unevaluated branches already return clean dirt.

### Boolean operators

Under lazy evaluator semantics:

```python
V(a and b) = V(a) and V(b)
D(a and b) = D(a) or D(b)
```

and:

```python
V(a or b) = V(a) or V(b)
D(a or b) = D(a) or D(b)
```

This works because if `b` is not evaluated, `D(b)` is already clean/false.

### Conditional expression

For:

```python
x if cond else y
```

the transform is:

```python
V = V(x) if V(cond) else V(y)
D = D(cond) or D(x) or D(y)
```

This is conservative but still correct under lazy evaluator semantics, because the untaken branch contributes clean dirt and does not imply semantic evaluation of both branches.

### Function calls

For plain non-slot calls:

```python
V(f(a, b)) = f(V(a), V(b))
D(f(a, b)) = D(a) or D(b)
```

For slot-bearing calls:

```python
V = vi.eval()
D = vi.dirty()
```

### Multi-result calls

For:

```python
val, func = use_state(3)
```

the evaluator returns structured value and structured dirt:

```python
V = v1.eval()      # e.g. (val, func)
D = v1.dirty()     # e.g. (dirty_val, dirty_func)
```

No special dirty transform is required beyond preserving the same structural shape.

## Walrus Transform

Walrus expressions are explicitly out of scope for Phase 1 when the expression contains slot-bearing calls.

Example:

```python
(var := use_grip(STORE)) + 10
```

Phase 1 rule:

- if the compiler encounters a walrus operator inside a slot-bearing expression transform
- it should raise an unsupported-form diagnostic
- the diagnostic should point at the walrus operator location

Conceptually:

- "slot-bearing expressions do not support walrus operators in Phase 1"

This avoids forcing a statement-level scope-binding rewrite into the initial `slot_expr` implementation.

## Final Binding

The final binding of:

- returned logical value(s)
- final dirty state for target names

is a separate call:

```python
.apply_dirt_sink(dirt_sink)
.evaluate("value")
```

or:

```python
.apply_dirt_sink(dirt_sink)
.evaluate("value")
```

or:

```python
.apply_dirt_sink(dirt_sink)
.evaluate("val", "func")
```

Return names are not part of call-site evaluation. They are only part of final target binding.

`apply_dirt_sink(dirt_sink)` is required in the model. The sink is the scoped object whose named fields are updated when `evaluate(...)` binds final results.

## Example: Single Scalar Result

Source:

```python
value = use_grip(STORE) or "clock"
```

Conceptual lowering:

```python
value = (
    slot_ctx
    .slot_expr(
        lambda v1: v1.eval() or "clock",
        lambda v1: v1.dirty(),
    )
    .slot_call(
        "v1",
        use_grip,
        lambda: slot_params(STORE),
        lambda: slot_params_dirt(slot_ctx.literal("clock").dirty),
    )
    .apply_dirt_sink(dirt_sink)
    .evaluate("value")
)
```

Semantics:

- `slot_call("v1", ...)` defines a call site
- the value lambda computes the expression result
- the dirty logic computes final dirtiness for `"value"`
- `apply_dirt_sink(dirt_sink)` attaches the scoped sink that will receive final dirtiness
- `evaluate("value")` binds:
  - the logical value
  - `dirt_sink.value`

And:

- `v1` is evaluated only if the expression requests it
- the call site is memoized after first use

## Example: True Tuple Return

Source:

```python
val, func = use_state(3)
```

Conceptual lowering:

```python
val, func = (
    slot_ctx
    .slot_expr(
        lambda v1: v1.eval(),
        lambda v1: v1.dirty(),
    )
    .slot_call(
        "v1",
        use_state,
        lambda: slot_params(3),
        lambda: slot_params_dirt(dm.__pyr_literal()),
    )
    .apply_dirt_sink(dirt_sink)
    .evaluate("val", "func")
)
```

Important:

- `use_state(3)` still logically returns two values
- the dirty result must have the same structural shape
- `apply_dirt_sink(dirt_sink)` provides the scoped dirtiness target
- `evaluate("val", "func")` destructures:
  - logical values
  - final dirty state for `val` and `func` onto `dirt_sink.val` and `dirt_sink.func`

This means:

- user-visible tuple returns stay tuple returns
- only the hidden dirty side channel is redesigned

## Example: Multiple Slot Calls

Source:

```python
total = use_grip(A) + use_grip(B)
```

Conceptual lowering:

```python
total = (
    slot_ctx
    .slot_expr(
        lambda a, b: a.eval() + b.eval(),
        lambda a, b: a.dirty() or b.dirty(),
    )
    .slot_call(
        "a",
        use_grip,
        lambda: slot_params(A),
        lambda: slot_params_dirt(dm.A),
    )
    .slot_call(
        "b",
        use_grip,
        lambda: slot_params(B),
        lambda: slot_params_dirt(dm.B),
    )
    .apply_dirt_sink(dirt_sink)
    .evaluate("total")
)
```

This shows why the expression model scales better than ad hoc hoisting:

- multiple calls become multiple evaluators
- the source expression shape is preserved
- final dirty logic can still be centralized
- only the calls actually requested by expression semantics are evaluated

## Dirtiness Management

The missing piece is how dirtiness is stored and updated.

The preferred model is:

- routing is precomputed by the compiler
- a dirtiness management object is created for the `slot_expr`
- each call-site evaluator updates that dirtiness manager during evaluation
- `apply_dirt_sink(dirt_sink)` attaches the scoped output sink
- final dirty state for bound names is written to that sink at `evaluate(...)`

This is better than:

- hidden extra return values
- a vague global mutable sink

because it keeps dirtiness tied to:

- the current slot
- the current expression
- the current call-site set

## Routing

What really needs to be precomputed is not “dirty flags in general,” but the mapping between:

- call-site parameters
- source arguments
- final dirty tracking names

This routing data should be available to the dirtiness manager before evaluation starts.

That way the runtime can update dirtiness in a way that matches:

- bound parameter names
- return shape
- final assigned target names

Each `slot_call(...)` therefore needs both:

- a lazy value-parameter lambda
- a lazy dirty-parameter lambda

Conceptually:

```python
.slot_call(call_id, func, args_lambda, dirt_args_lambda)
```

where:

- `args_lambda` produces the value-side bound call parameters
- `dirt_args_lambda` produces the corresponding dirty-side parameter mapping

This keeps value and dirt routing paired at the call-site boundary.

`slot_params_dirt(...)` should mirror the normal parameter binding shape exactly.

Examples:

```python
slot_params(prefix, label=name, visible=True)
slot_params_dirt(dm.prefix, label=dm.name, visible=dm.__pyr_literal())
```

That means:

- positional dirty parameters align with positional value parameters
- keyword dirty parameters align with keyword value parameters
- constants and literals are dirty on initial render only
- constants and literals are clean on rerenders

## Dirtiness Sink

The dirtiness sink is the scoped object that receives final expression dirtiness for the names passed to `evaluate(...)`.

Example:

```python
value = (
    slot_ctx
    .slot_expr(
        lambda v1: v1.eval() or "clock",
        lambda v1: v1.dirty(),
    )
    .slot_call(
        "v1",
        use_grip,
        lambda: slot_params(STORE),
        lambda: slot_params_dirt(dm.__pyr_literal()),
    )
    .apply_dirt_sink(dirt_sink)
    .evaluate("value")
)
```

After evaluation:

- `value` holds the logical expression result
- `dirt_sink.value` holds the final dirtiness for that bound result

Likewise:

```python
val, func = (
    slot_ctx
    .slot_expr(
        lambda v1: v1.eval(),
        lambda v1: v1.dirty(),
    )
    .slot_call(
        "v1",
        use_state,
        lambda: slot_params(3),
        lambda: slot_params_dirt(dm.__pyr_literal()),
    )
    .apply_dirt_sink(dirt_sink)
    .evaluate("val", "func")
)
```

After evaluation:

- `val`, `func` hold the logical results
- `dirt_sink.val`, `dirt_sink.func` hold the corresponding final dirtiness

This is the key mapping:

- `apply_dirt_sink(...)` provides the scoped destination
- `evaluate(*names)` provides the output names
- the runtime binds final dirty results onto the sink under those names

## Return Shape

One important rule:

- the dirty result should have the same structural shape as the logical value result

Examples:

- scalar value => scalar dirty result
- tuple value => tuple dirty result

Then `evaluate(...)` handles:

- one target name: collapse/bind scalar result
- many target names: destructure tuple-shaped result

## Dirt Binding Semantics

`evaluate(...)` is responsible for both:

- binding the logical value result
- binding the final dirty result onto the attached dirtiness sink

### Single target

For:

```python
.evaluate("result")
```

the runtime should:

- bind the logical value to `result`
- bind the dirty result, in its full structural shape, to `dirt_sink.result`

Example:

```python
result = (
    slot_ctx
    .slot_expr(
        lambda v1: v1.eval(),
        lambda v1: v1.dirty(),
    )
    .slot_call(
        "v1",
        use_state,
        lambda: slot_params(3),
        lambda: slot_params_dirt(dm.__pyr_literal()),
    )
    .apply_dirt_sink(dirt_sink)
    .evaluate("result")
)
```

After evaluation:

- `result` might be `(val, func)`
- `dirt_sink.result` should be the matching dirty tuple, for example `(True, False)`

### Multiple targets

For:

```python
.evaluate("val", "func")
```

the runtime should:

- destructure the logical value result
- destructure the dirty result in parallel
- bind:
  - `val`, `func`
  - `dirt_sink.val`, `dirt_sink.func`

Example:

```python
val, func = (
    slot_ctx
    .slot_expr(
        lambda v1: v1.eval(),
        lambda v1: v1.dirty(),
    )
    .slot_call(
        "v1",
        use_state,
        lambda: slot_params(3),
        lambda: slot_params_dirt(dm.__pyr_literal()),
    )
    .apply_dirt_sink(dirt_sink)
    .evaluate("val", "func")
)
```

### Binding rule

So the binding rule is:

- one output name: store the whole dirty shape under that one name
- many output names: unpack dirty shape structurally across those names

The sink therefore needs an assignment-shaped binding surface, conceptually like:

```python
dirt_sink.bind.value = True
dirt_sink.bind.val, dirt_sink.bind.func = (True, False)
del dirt_sink.bind.value
```

`evaluate(...)` should still own the structural unpacking logic, but the sink itself should look like ordinary binding rather than a custom public `bind_many(...)` API.

### Rerender shape preservation

On rerender, a slot expression may reuse cached results or avoid re-executing some underlying slot-bearing calls.

Even then:

- the dirty result shape must still exist
- the shape must match the logical value shape
- the shape must be populated with clean/false entries when nothing is dirty

So the runtime needs a way to preserve or reconstruct:

- tuple dirty shape
- nested container dirty shape
- scalar dirty shape

without requiring every call site to be re-executed.

### Container dirt checks

Dirty checks must be structural.

If a dirty result is a container:

- tuple
- list
- dict
- other structured dirty shape

then checking whether the result is dirty must inspect the contained dirty flags, not the container object itself.

In other words:

- a tuple dirty result is dirty if any contained element is dirty
- a list dirty result is dirty if any contained element is dirty
- a dict dirty result is dirty if any contained value is dirty

The container object existing is not itself the dirty signal.

Conceptually:

```python
is_dirty(False) -> False
is_dirty((False, False)) -> False
is_dirty((True, False)) -> True
is_dirty({"a": False, "b": True}) -> True
```

This rule is important both for:

- runtime dirt application
- any later `if dirt_sink.value:` style checks

### Phase 1 boundary

In Phase 1, only `slot_expr.evaluate(...)` should bind dirt onto named outputs.

If user code later does:

```python
val, func = result
```

after:

```python
result = slot_expr(...).evaluate("result")
```

that later destructuring is ordinary Python destructuring, not automatic dirt rebinding.

If named dirt is required for `val` and `func`, the slot expression should bind them directly with:

```python
.evaluate("val", "func")
```

## Dirty Manager

The design needs one consistent way to answer:

- "what is the dirtiness of this source value at this point in the slot?"

The recommended answer is:

- use the dirt manager directly as the single source of truth for bound dirt values

In lowered compiler output this should be a single central manager for the function scope:

- `__pyr_dm`

In examples below, `dm` is used as the human-readable stand-in for that lowered symbol.

## Dirt Manager Lookup Rules

### Literals and constants

Literals/constants should be dirty on initial render only, using the existing slot-context literal surface.

Conceptually:

```python
slot_ctx.literal(3).dirty
```

This is the dirt-manager surface for "dirty on initial render only".

Examples:

```python
slot_ctx.literal(3).dirty  # for 3
slot_ctx.literal(True).dirty  # for True
slot_ctx.literal("clock").dirty  # for "clock"
```

### Globals

Globals should use the same default behavior as literals in Phase 1.

That is:

- assume global values are stable
- mark them dirty only on initial render

Conceptually:

```python
slot_ctx.literal(GLOBAL_LABEL).dirty  # when the source term is a global
```

This is intentionally conservative and simple.

### Locals

Locals should default to dirty unless overridden by tracked binding.

Conceptually:

```python
dm.bind.local_name
```

or more abstractly:

```python
dm.lookup("local_name")
```

with the default rule:

- locals are dirty unless there is explicit tracked dirt metadata saying otherwise

This default matters because ordinary local expressions often derive from values that have already changed in the current render.

### Slot-expression-bound names

If a local is produced by:

- `slot_expr.evaluate(...)`
- structural unpacking performed by `evaluate(...)`

then that binding overrides the default local rule.

Examples:

```python
value = slot_expr(...).evaluate("value")
```

means:

- `dm.bind.value` is whatever the slot expression bound

and:

```python
val, func = slot_expr(...).evaluate("val", "func")
```

means:

- `dm.bind.val`
- `dm.bind.func`

are explicitly bound from that expression's dirty result

### Unpackings

Tracked unpacking should also write through the dirt manager.

For example, when `evaluate("val", "func")` destructures a tuple result, it should:

- bind the logical values
- bind `dm.bind.val`
- bind `dm.bind.func`

This is one of the main ways a local stops using the default "dirty unless overridden" rule.

## Practical Dirty Manager Examples

Given:

```python
GLOBAL_LABEL = "clock"
prefix = "x"
value = slot_expr(...).evaluate("value")
```

the Phase 1 model should behave like:

```python
slot_ctx.literal(GLOBAL_LABEL).dirty  # for GLOBAL_LABEL
dm.bind.prefix  # default local path
dm.bind.value   # explicit slot_expr binding
```

And for:

```python
val, func = slot_expr(...).evaluate("val", "func")
```

the model should behave like:

```python
dm.bind.val
dm.bind.func
```

## Why This Matters

This gives one uniform rule for building `slot_params_dirt(...)`:

- literals/constants: `slot_ctx.literal(value).dirty`
- globals: `slot_ctx.literal(global_value).dirty`
- locals: `dm.bind.name`
- slot-expression outputs/unpacked names: whatever explicit dirty binding was written there

That should make compiler lowering much simpler and more predictable.

## Lazy Argument Production

Each `slot_call(...)` should take a lazy argument lambda rather than eager arguments.

Conceptually:

```python
.slot_call(
    "v1",
    use_grip,
    lambda: slot_params(STORE),
    lambda: slot_params_dirt(slot_ctx.literal("clock").dirty),
)
```

This matters because:

- call arguments should only be produced if the call site is actually evaluated
- argument evaluation should follow the same laziness boundary as the call site itself
- it leaves room for nested slot-bearing arguments later

And the dirty-side argument mapping should be produced lazily for the same reason.

The argument lambda may eventually need access to earlier evaluators for nested slot-bearing arguments, for example:

```python
.slot_call(
    "v2",
    helper,
    lambda v1: slot_params(v1.eval()),
    lambda v1: slot_params_dirt(v1.dirty()),
)
```

That detail is still open, but the model should assume lazy argument production from the start.

## Component Parameters With Slot Calls

Parameters to component functions (`@pyrolyze` functions or `ComponentRef` calls) that themselves contain slot-bearing expressions should be treated as a distinct slot-expression call scope.

That means:

- slot-bearing component arguments are not just ordinary values
- they need their own slot-expression treatment at the call boundary
- the argument slot-expression writes through the same function-level dirt manager (`__pyr_dm`)
- call-site ids for those argument-local slot calls are compiler-generated the same way as any other slot-expression call-site ids
- the bound argument value produced by that slot expression is what is passed to the component call
- the bound dirt result produced by that slot expression is what updates the relevant names on `__pyr_dm`

This should be modeled consistently with ordinary slot-bearing expressions, not as a special one-off path.

## Pass Staging And Commit

`SlotExpr` should behave as a staged per-pass transaction.

For each pass:

1. begin expression pass
2. lazily evaluate reachable call sites
3. stage:
   - updated call-site state
   - newly created registrations/subscriptions/effects/adverts
   - deactivations for previously-live but now-unvisited call sites
   - final dirty bindings for `evaluate(...)`
4. if evaluation succeeds:
   - commit staged call-site updates
   - commit staged registrations/deactivations
   - commit final dirty bindings
5. if evaluation fails:
   - discard staged updates
   - discard staged deactivations
   - discard staged final dirt bindings
   - preserve the previously committed state

This means:

- expression exceptions abort the whole `SlotExpr` pass
- partial evaluation must not leak partially-updated bindings
- deactivation is a staged lifecycle effect, not an immediate side effect

## Reachability And Deactivation

Call-site liveness follows actual evaluation reachability.

That means:

- a call site visited on the current successful pass stays live
- a call site that was live in the previous committed pass but is not visited in the current successful pass must deactivate
- deactivation is applied only on the successful commit boundary

Example:

```python
ab = use_grip(A) or use_grip(B)
```

Pass 1:

- `A` is falsy
- `B` is evaluated
- `B` becomes live

Pass 2:

- `A` is truthy
- `B` is not evaluated
- after successful pass commit, `B` deactivates

This is equivalent in liveness terms to:

```python
ab = use_grip(A)
if not ab:
    ab = use_grip(B)
```

By contrast, eager forms keep all calls reachable:

```python
ab = any((use_grip(A), use_grip(B)))
```

or:

```python
a = use_grip(A)
b = use_grip(B)
ab = a or b
```

Those evaluate both call sites every pass, so both remain live.

## Handler Parity With plain_call

`SlotCallEvaluator` needs the full semantic coverage of the current `plain_call` handler family:

```python
_PLAIN_CALL_HANDLERS = (
    ExternalStoreHandler(),
    PyrolyzeMountAdvertisementHandler(),
    UseEffectAsyncHandler(),
    UseEffectHandler(),
    PlainValueHandler(),
)
```

This means `SlotExpr` should not only reproduce value projection. It should also reproduce the lifecycle semantics of those handlers, including:

- external store refresh without reinvoking the original callable
- staged registration and deregistration
- effect/update staging
- advertisement staging
- plain value rebinding

The handler/binding infrastructure should be extracted from `runtime/context.py` and reused or mirrored in a way that preserves those semantics.

## Registration Pairing And Reference Retention

Registration and deactivation must pair on commit boundaries.

That means:

- no registration/subscription/effect activation should become committed without a matching later deactivation path
- no deactivation of previously-committed state should happen before successful pass commit
- lifecycle transitions should be staged and committed atomically

Also:

- `SlotCallEvaluator` should expose dereferenced logical values to the expression
- binding objects may retain lifecycle state where required
- but raw returned values should not be retained more broadly than necessary, to avoid unnecessary reference retention and leaks

## What This Simplifies

If this model works, it removes pressure to solve every expression case by hoisting.

It should make:

- boolean expressions
- coercions
- nested expressions
- multiple slot calls in one expression
- mixed value/dirty control flow

much more natural to represent.

## What Remains Hard

### 1. Dirty Lambda Semantics

This is the most important rule to lock.

The chosen rule is:

- if a call site is not evaluated by the value expression, its dirty result is clean
- an unevaluated call site must not force evaluation just to answer `dirty()`

So under short-circuit/control-flow:

- unevaluated branch => clean dirty result
- evaluated branch => its actual dirty result

That means `dirty()` must respect the value path rather than independently forcing computation.

For:

```python
value = use_grip(STORE) or "clock"
```

if `v1.eval()` is never reached, then:

```python
v1.dirty() -> False
```

or the matching clean structural shape.

### 2. Unevaluated Shape

Unevaluated results still need a shape.

The chosen model is:

- use a special unevaluated placeholder/container
- when unpack/bind occurs, every destination receives clean/false dirt

So an unevaluated tuple-like result behaves like:

- value side: not materially consumed unless the expression requests it
- dirt side: clean in every bound destination

This gives a stable way to support:

- tuple destructuring
- rerender clean state
- skipped branches

without forcing reevaluation.

### 3. Nested Slot-Bearing Arguments

These are in scope.

The chosen model is:

- recursively split the expression AST at slot-bearing call sites
- each lambda gets the evaluator parameters it depends on
- maintain a mapping from lambda nodes to the evaluator call sites they need

So nested slot-bearing arguments are handled by the same rule, recursively, rather than being forbidden.

### 4. Walrus Operator

Walrus expressions containing slot-bearing calls are unsupported in Phase 1.

The compiler should raise an unsupported-form diagnostic at the walrus operator location with wording equivalent to:

- "slot-bearing expressions do not support walrus operators in Phase 1"
### 5. Stable Call-Site Identity

Call sites are not child slots, but they still need stable identities inside the parent slot so rerendering can match them.

### 6. Multi-Return Logical Values

Calls like `use_state(...)` must remain natural tuple returns while still integrating with the expression dirtiness model.

### 7. Dirt Manager Scoping Rules

The dirt manager should follow the same binding semantics as value bindings.

That means:

- reassignment reassigns dirt in parallel
- shadowing shadows dirt the same way it shadows values
- explicit deletion should delete dirt too

Conceptually:

```python
del var
```

maps to deletion through the dirt-manager binding surface:

```python
del __pyr_dm.bind.var
```

Tuple unpacks outside `evaluate(...)`, attribute writes, and subscript writes are part of Phase 1. The general principle is:

- dirt follows value-binding semantics unless the design explicitly restricts the form

That means:

- `obj.attr = value` should update dirt in parallel with the attribute write
- `obj[key] = value` should update dirt in parallel with the subscript write
- keyed loop machinery may need to carry both container value and container dirt so attribute/subscript assignment inside keyed bodies can preserve the same semantics

### 8. `evaluate(...)` Structure Contract

`evaluate(...)` must be strict about shape.

Current direction:

- mismatch should raise
- errors should use the same file/line/code reporting style as the existing AST transform

This includes cases like:

- value shape does not match target arity
- dirty shape does not match value shape
- nested tuple destructuring shape mismatch

Nested tuple shapes are allowed if the runtime binding surface supports them, but the matching rules must be exact.

### 9. Component Argument Boundaries

Slot-bearing expressions passed into component calls need their own call-scope handling.

Operationally, this means:

- a component argument containing slot-bearing calls should be lowered as its own slot expression
- that slot expression becomes part of the argument-evaluation boundary for the component call
- that slot expression still writes through the same central function dirt manager (`__pyr_dm`)
- the compiler owns the call-site id allocation for those argument-local slot calls
- the resulting bound argument values are what flow into the component invocation

This is not a separate conceptual system. It is the same slot-expression model applied at the component-argument boundary.

## Phase 1 Restriction: No Slot Calls In Comprehensions

Phase 1 should explicitly reject slot-bearing comprehensions.

Examples:

```python
stuff = {k: use_grip(k) for k in keyed(keys, key=lambda k: k)}
vals = [use_grip(k) for k in keyed(keys, key=lambda k: k)]
```

Reason:

- comprehensions combine implicit iteration scope with expression lowering
- slot-bearing repeated structure already has a keyed-loop model
- adding comprehension support during the expression-model redesign would mix two hard problems

So for Phase 1:

- keyed `for` loops only
- no slot-bearing comprehensions

Diagnostics for rejected forms should use the same error-reporting scheme already used by the AST transform, including stable error codes and source locations.

## Keyed Comprehensions (Deferred)

Keyed comprehensions can be revisited later.

If they are explored, they should likely lower to keyed loop machinery rather than being treated as ordinary Python comprehensions.

But that is explicitly not part of this design.

## Design Summary

This document defines the Phase 1 direction as:

- remove old `plain_call`-style slot expression lowering
- introduce `slot_expr`
- represent each slot-bearing call as a call site evaluator inside the current slot
- evaluate the source expression through lazy, memoized evaluators
- compute final dirtiness through runtime-managed expression dirtiness
- bind logical values and dirty state at `evaluate(...)`
- defer slot-bearing comprehensions entirely
