# UIKit PyRolyze Feasibility

## Purpose

Assess whether PyRolyze can support an iOS UIKit backend driven by a Python
reactive runtime on a background thread while keeping all UIKit mutation on the
main thread.

This memo does not propose shipping code yet. It defines the most plausible
architecture, the main failure modes, and the constraints that should shape a
future backend.

## Short Answer

Yes, PyRolyze can plausibly support UIKit, but only if the UIKit backend is
treated as a constrained native host with explicit lifecycle, scheduling, and
metadata rules.

The backend should **not** behave like a transparent "Python owns UIKit object
graphs directly" bridge.

Instead:

- Python owns authored state, slot invalidation, and commit planning.
- UIKit owns concrete views, controllers, layout, and event ingress.
- The bridge carries compact commit payloads and opaque native handles.
- Event callbacks route through retained native proxy objects, then enqueue work
  back to the Python runtime.

If PyRolyze follows that shape, the model is feasible. If it instead tries to
expose the full UIKit surface as a wide, eager, per-call dynamic bridge, it
will likely hit the same startup, memory, lifecycle, and latency ceilings seen
in earlier cross-runtime UI systems.

## Why UIKit Is A Good Fit For PyRolyze

PyRolyze already has traits that line up well with native UI hosting:

- slot-based identity
- owner-scoped reconciliation
- explicit invalidation scheduling
- native backend adapter boundaries
- non-VDOM reactive updates

Those properties are useful on iOS because UIKit rewards narrow, stable, and
predictable mutation sets. A PyRolyze backend can preserve that advantage if it
crosses the Objective-C boundary with already-coalesced native commit records
rather than a stream of tiny imperative calls.

The core feasibility question is therefore not "can Python talk to UIKit?".
That is established by Rubicon-ObjC, PyObjC, BeeWare, NativeScript, Titanium,
and React Native's historical use of bridged native modules.

The real question is:

- can PyRolyze keep ownership correct across ARC and Python GC?
- can it keep the main run loop from being flooded?
- can it route events safely without relying on brittle executable trampolines?
- can it expose enough UIKit metadata without paying the cost of loading all of
  UIKit eagerly?

The rest of this memo answers those questions in PyRolyze terms.

## Proposed Architectural Shape

### 1. Runtime Partition

Recommended partition:

- background thread
  - PyRolyze slot evaluation
  - dependency tracking
  - invalidation scheduling
  - diff / commit planning
- main thread
  - UIKit object creation
  - property mutation
  - containment / hierarchy changes
  - Auto Layout interaction
  - event ingress from UIKit

This partition is stricter than the current desktop backends, but it fits iOS
better.

### 2. Backend Contract

A UIKit backend should consume a committed PyRolyze UI snapshot and derive a
small number of native operations:

- create node
- dispose node
- attach / detach child
- update mutable property set
- replace event binding
- perform layout-affecting structural change

That contract should remain declarative and identity-based. It should avoid
turning each authored API call into a direct bridge invocation.

### 3. Identity Model

Use existing PyRolyze identity concepts as the primary backend keys:

- `slot_id`
- owner slot lineage
- keyed child path where relevant
- backend-local node token

UIKit objects should be indexed by stable PyRolyze node identity, not by the
temporary identity of Python wrapper objects.

## Ownership And Lifetime Model

### Core Rule

One system must be the practical owner of native objects. For UIKit, that
should be UIKit plus the backend's mounted-node registry, not transient Python
objects.

Recommended model:

- UIKit hierarchy strongly owns views through normal parent/child retention.
- PyRolyze backend registry strongly owns bridge proxies and mounted-node state.
- Python wrappers hold either opaque handles or carefully managed references.
- delegate and target-action proxies are retained explicitly by backend state.

### Why This Matters

ARC and Python GC have different visibility into the full graph. A cross-runtime
cycle can survive even when each side looks correct locally.

Bad shape:

- Python wrapper strongly references a `UIView`
- `UIView` or related helper strongly references a Python callback or wrapper
- cleanup depends on Python finalization timing

Better shape:

- mounted backend state strongly owns a delegate/target proxy
- proxy weakly references higher-level Python owner state where possible
- unmount explicitly disconnects native callbacks and releases proxy retention

### Delegate And Target Retention

UIKit often keeps delegates weak. That means a Python-defined or bridge-defined
delegate cannot rely on UIKit to keep it alive.

PyRolyze should therefore keep a strong backend-side registry:

- key: mounted node identity
- value: proxy object(s), event routing token, cleanup metadata

That registry should be updated during reconcile and cleared during unmount.

### Do Not Rely On Finalizers For Correctness

Finalizers are acceptable only as leak detection or last-resort cleanup.
Correctness should come from explicit lifecycle:

- mount
- update
- disconnect
- dispose

If disposal depends on Python GC eventually discovering an unreachable cycle,
the backend will be difficult to reason about and likely leak under stress.

### Autorelease Pools

If background Python threads invoke Objective-C or Foundation APIs during
planning, the bridge needs a disciplined autorelease-pool story for those
threads. Even if UIKit mutation stays on main, temporary Objective-C objects can
still accumulate on bridge/helper threads if autorelease pools are not drained
predictably.

## Scheduling And Commit Strategy

### Main Risk

The biggest performance risk is not Python compute alone. It is excessive
cross-thread, cross-runtime dispatch granularity.

Bad pipeline:

- one state change
- one dispatch to main
- one or two UIKit setters
- repeat hundreds of times per interaction burst

That shape wastes the advantage of slot-level invalidation and can starve the
main run loop.

### Recommended Commit Model

The background runtime should accumulate dirty slots and produce a bounded UI
commit per owner region or mounted root. The main thread should receive commits,
not raw invalidations.

One commit should support:

- deduped property writes
- last-writer-wins collapsing within the same cycle
- ordered structural edits
- event-subscription diffs
- explicit remount markers when constructor-only values changed

### Coalescing Policy

Recommended rules:

- at most one outstanding unprocessed commit per owner region
- newer commits supersede stale queued commits when safe
- repeated writes to the same node/prop collapse before crossing the bridge
- structural changes and value changes are computed together so the main thread
  sees a coherent patch

### Frame And Runloop Awareness

PyRolyze does not need a per-frame renderer, but it does need runloop awareness.
On iOS, dispatch frequency should be treated as part of the performance budget.

Good practice:

- align commit application to runloop turns where possible
- prioritize input echo and visible interaction paths
- avoid shipping cosmetic churn while text entry or gestures are active

### Event Round-Trip Discipline

Event delivery should be asymmetrical:

- UIKit event enters on main
- native proxy packages minimal payload
- payload is enqueued to Python runtime
- Python may produce zero or more UI changes
- resulting UI changes return later as one coalesced commit

Do not run authored Python event logic inline on the main thread unless a
future design explicitly introduces a tightly bounded synchronous fast path.

## Callback Routing And Native Proxy Strategy

### Recommended Pattern

Use a small set of fixed native proxy classes or shim methods compiled into the
app, each forwarding into a backend registry.

That registry maps:

- native proxy instance
- selector / event kind
- mounted node identity
- Python event target token

This is more robust than generating large numbers of ad hoc executable
callbacks.

### Why Fixed Native Shims Are Preferable

Apple platform security places meaningful constraints around executable memory
and JIT-like behavior. libffi has evolved to handle Apple platforms better, but
it should be treated as a low-level mechanism, not the center of the backend
design.

A compiled-shim design has advantages:

- less dependence on runtime-generated executable trampolines
- clearer lifecycle
- easier crash diagnosis
- easier static analysis of callback shapes
- reduced exposure to iOS security-policy changes

### W^X / Executable Memory Implication

The backend should assume that callback machinery depending on dynamically
generated executable pages is a risk surface. Even if a given bridge stack can
make it work today, PyRolyze should architect around fixed native entry points
and data-driven dispatch.

That is the safest long-term choice for App Store-facing iOS work.

## API Surface Strategy

### Do Not Start With "Expose All Of UIKit"

A full dynamic language projection of UIKit is possible, but that is the wrong
first target for PyRolyze.

PyRolyze needs:

- a stable authored surface
- a stable backend registry
- a finite first-party widget set
- explicit property and event semantics

That argues for a curated surface first, not universal native exposure.

### Metadata Strategy

Use a hybrid model:

- static metadata generation for method signatures, property shape, ownership
  semantics, block signatures, enums, and constants where runtime metadata is
  incomplete
- live Objective-C runtime introspection for availability checks, protocol/class
  lookup, and late binding where safe
- lazy loading of metadata and wrappers on first use

### Why Hybrid Is Better

The Objective-C runtime alone is not enough to bind everything correctly.
Historical Apple BridgeSupport metadata and PyObjC's compiled metadata system
both exist because runtime introspection does not fully describe all ABI
details.

At the same time, loading a complete UIKit surface eagerly has real cost:

- slower startup
- larger memory footprint
- more symbol and metadata churn
- more difficult debugging when large numbers of wrappers are live

### PyRolyze-Specific Recommendation

Split the API into three layers:

1. author-facing semantic UI library
2. backend registration / generated metadata surface
3. runtime-only bridge helpers

That matches the existing repo guidance to keep authored API, registration
manifests, and runtime internals distinct.

For UIKit, that likely means:

- author-level `UIKitUiLibrary` or equivalent semantic surface
- generated native descriptor catalog for supported widgets/properties/events
- internal Objective-C bridge and event proxy helpers hidden from authored code

## Mapping UIKit Into PyRolyze Concepts

### Views

UIKit views fit naturally into mounted nodes.

Recommended mapping:

- one mounted node owns one primary UIKit object
- backend spec decides which props are mutable versus remount-only
- child management maps to subview containment or controller containment rules

### View Controllers

`UIViewController` should not be treated as interchangeable with a view node.
It should have explicit backend semantics because containment, lifecycle, and
presentation rules differ from plain view composition.

Likely rule:

- first backend phase targets view-backed widget composition
- controller-backed surfaces come later as explicit container constructs

### Auto Layout

Auto Layout can be used, but it changes the mutation cost model.

Guidelines:

- keep layout-affecting changes distinct from cosmetic property updates
- avoid repeated constraint churn during high-frequency update bursts
- prefer stable constraint graphs with changing constants over destroy/recreate
  loops

This should influence which props are marked remount-only versus updateable in
the backend spec.

### Lists / Reuse

UIKit collection and table infrastructure introduces reuse semantics that are
not identical to ordinary subview trees.

PyRolyze should not fake these as naive nested child lists. It will likely need
specialized adapters for:

- list cell identity
- reuse lifecycle
- event routing through reused cells
- data-source/delegate ownership

This is a later-phase concern, but it should be planned early because reuse is
one of the first places where slot identity and UIKit identity can drift apart
if the backend model is too simplistic.

## Historical Lessons From Other Systems

### React Native

Relevant lesson:

- the old async bridge avoided blocking the UI thread
- but large numbers of serialized bridge messages added latency and overhead
- the newer architecture moved toward direct interop, lazy loading, and better
  scheduling

PyRolyze should learn from this by ensuring that its slot-based runtime produces
fewer, richer commits rather than many tiny bridge calls.

### BeeWare / Rubicon-ObjC / Toga

Relevant lesson:

- Python-to-UIKit orchestration is viable
- lifetime and delegate retention are the sharp edges
- metadata and type handling matter

PyRolyze should assume lifecycle discipline is a first-order design constraint,
not a cleanup concern for later.

### NativeScript

Relevant lesson:

- pre-generated metadata and direct native access can work well
- but memory management and delegate ownership remain sharp
- exposing a huge native surface has startup and footprint implications

PyRolyze should copy the metadata and lazy-loading discipline, not the ambition
to make all of UIKit equally dynamic from day one.

### Titanium / Hyperloop

Relevant lesson:

- wide native exposure is powerful
- but toolchain sensitivity, startup regressions, and maintenance overhead
  increase quickly

PyRolyze should prefer a narrow, well-defined backend contract over a universal
dynamic projection of Apple frameworks.

## Feasibility Assessment By Pillar

### Memory Management

Feasible if:

- delegate and callback proxies are retained explicitly
- cross-runtime cycles are minimized
- unmount performs deterministic teardown
- native objects are owned by backend-mounted state and UIKit hierarchy, not by
  incidental Python wrappers

High risk if:

- Python wrappers strongly own native objects bidirectionally
- cleanup relies on finalizers
- callbacks are not disconnected at unmount

### Threading

Feasible if:

- Python computes off-main
- main thread receives coalesced commits
- events are converted to small payloads then offloaded

High risk if:

- every slot invalidation becomes its own GCD hop
- text/gesture paths cause repeated property writes with no coalescing

### Callback Mechanism

Feasible if:

- fixed native proxies or compiled shims are used
- callback routing is registry-driven
- libffi is treated as a low-level implementation detail only where necessary

High risk if:

- backend depends broadly on dynamically generated executable trampolines
- callback identity and lifecycle are implicit

### API Exposure

Feasible if:

- metadata is generated ahead of time
- wrappers are loaded lazily
- first-party surface is curated

High risk if:

- UIKit is exposed eagerly and wholesale
- runtime introspection is expected to recover all signature/ownership metadata

## Recommended Phase Plan

### Phase 0: Constraints Memo And Surface Definition

Define:

- initial supported UIKit widget set
- node identity mapping rules
- event proxy lifecycle rules
- remount-only versus mutable prop categories

Deliverable:

- backend design spec

### Phase 1: Bridge Kernel Spike

Build a minimal spike for:

- one root host
- a few basic views
- one control event path
- deterministic mount / update / dispose lifecycle

Success criteria:

- explicit retention model works
- no obvious leaks in repeated mount/unmount stress
- event callback round-trip works without main-thread Python execution

### Phase 2: Commit Queue And Coalescing

Introduce:

- background commit planning
- superseding commit queue
- owner-scoped batching
- stale-commit rejection

Success criteria:

- repeated state churn produces bounded main-thread work
- input responsiveness remains acceptable under bursty updates

### Phase 3: Metadata And Generated Surface

Add:

- generated native catalog
- lazy wrapper resolution
- curated author-facing semantic API

Success criteria:

- startup cost remains bounded
- adding supported widgets does not require hand-maintaining large dynamic glue

### Phase 4: Advanced Surfaces

Only after the basics are solid:

- Auto Layout-heavy containers
- controller containment
- list / collection abstractions
- gesture-heavy surfaces

## Recommended Non-Goals For The First UIKit Backend

Avoid promising these initially:

- universal dynamic access to all UIKit classes
- synchronous authored Python logic on the main thread
- broad support for arbitrary Objective-C delegate protocols
- general-purpose collection/table reuse abstraction without backend-specific
  modeling
- automatic binding of any Apple framework purely through runtime
  introspection

## Final Recommendation

UIKit support for PyRolyze is feasible and worth pursuing, but only under a
backend design that is stricter than typical desktop-native adapters.

The winning shape is:

- Python background runtime for state and diff planning
- main-thread-only UIKit mutation
- explicit mounted-node ownership and teardown
- retained native event proxies
- coalesced owner-scoped commits
- hybrid static-metadata plus lazy-runtime lookup
- curated first-party UIKit surface

The losing shape is:

- per-call bridge chatter
- eager full-UIKit exposure
- implicit delegate retention
- lifecycle cleanup deferred to GC
- heavy dependence on dynamically generated executable callbacks

If PyRolyze treats UIKit as a disciplined native commit target rather than a
fully transparent object graph, the architecture is credible.

## Sources

The design conclusions in this memo were informed by:

- Apple object ownership and delegation guidance
- Apple thread-safety and runloop / queue guidance
- Apple Objective-C runtime and BridgeSupport metadata history
- Apple documentation around executable-memory / JIT constraints
- Python GC and weakref documentation
- Rubicon-ObjC memory-management guidance
- PyObjC metadata-system documentation
- NativeScript metadata and memory-management documentation
- React Native new-architecture and bridgeless evolution notes
- Titanium Hyperloop documentation and release-history discussion

Key references:

- `developer.apple.com/library/archive/documentation/General/Conceptual/DevPedia-CocoaCore/ObjectOwnership.html`
- `developer.apple.com/library/archive/documentation/General/Conceptual/DevPedia-CocoaCore/Delegation.html`
- `developer.apple.com/library/archive/documentation/Cocoa/Conceptual/ProgrammingWithObjectiveC/WorkingwithProtocols/WorkingwithProtocols.html`
- `developer.apple.com/library/archive/documentation/Cocoa/Conceptual/Multithreading/ThreadSafetySummary/ThreadSafetySummary.html`
- `developer.apple.com/library/archive/documentation/General/Conceptual/ConcurrencyProgrammingGuide/OperationQueues/OperationQueues.html`
- `developer.apple.com/library/archive/documentation/Cocoa/Conceptual/MemoryMgmt/Articles/mmAutoreleasePools.html`
- `developer.apple.com/documentation/objectivec/objective-c-runtime`
- `developer.apple.com/library/archive/documentation/Cocoa/Conceptual/RubyPythonCocoa/Articles/GenerateFrameworkMetadata.html`
- `developer.apple.com/support/alternative-browser-engines-jp/`
- `docs.python.org/3/library/gc.html`
- `docs.python.org/3/library/weakref.html`
- `rubicon-objc.readthedocs.io/en/stable/how-to/memory-management.html`
- `rubicon-objc.readthedocs.io/en/stable/reference/rubicon-objc-api.html`
- `pyobjc.readthedocs.io/en/latest/metadata/`
- `pyobjc.readthedocs.io/en/latest/metadata/compiled.html`
- `docs.nativescript.org/guide/metadata`
- `docs.nativescript.org/guide/marshalling/`
- `old.docs.nativescript.org/core-concepts/memory-management`
- `docs.nativescript.org/best-practices/ios-tips`
- `reactnative.dev/blog/2024/04/22/release-0.74`
- `reactnative.dev/blog/2024/10/23/the-new-architecture-is-here`
- `titaniumsdk.com/guide/Titanium_SDK/Titanium_SDK_Guide/Hyperloop/Hyperloop_FAQ.html`
- `titaniumsdk.com/guide/Titanium_SDK/Titanium_SDK_Guide/Hyperloop/Hyperloop_Guides/iOS_Hyperloop_Programming_Guide/`
- `github.com/libffi/libffi`
