# AppKit Native Backend Project Plan

Status: design draft. No backend implementation or GUI acceptance is claimed.

Build a native macOS Pyrolyze backend using PyObjC and AppKit. Python continues
to execute reactive components and produce UI elements; the backend applies
those elements to native controls using the existing mountable engine. This is
an additional toolkit integration, not a new renderer, an Electron host, or a
replacement for Qt, Tkinter, or Dear PyGui.

The full public AppKit class inventory is **316 classes** for the installed
macOS 26.4 SDK. The first milestone is one working native form with retained
controls, correct child placement, and normal text editing. Its five native UI
classes and the twenty-class starter catalog below are implementation subsets,
not the final full-catalog count.

## Scope And Isolation

Implementation should run in an isolated Pyrolyze checkout with its own branch
and environment. Do not switch, reset, or install dependencies into the live
checkout used by the lifecycle and catalog-loading agents. Pin the starting
revision and dependency versions in the implementation evidence.

The lifecycle integration and existing lazy-loading changes remain independent.
Consume their accepted interfaces; do not modify transaction ownership,
completion, compiler routing, or another toolkit's catalog as incidental work.
If a shared interface genuinely needs extending, present the concrete AppKit
counterexample and a bounded proposal before expanding the scope.

In scope for the first milestone:

- A macOS-only optional backend and native window host.
- View and stack containers, buttons/toggles, labels, and text fields.
- Explicit native descriptors and the existing author-facing native-call model.
- Main-thread native application, retained updates, ordered placement, callbacks,
  disposal, and visible interaction verification.
- Demand-loaded definitions using the existing native-library loading machinery.

Not in scope:

- New FFI bindings, SwiftUI, or complete AppKit coverage.
- A reconciliation rewrite, Rust core, or worker-thread reactive runtime.
- Pixel-identical portability or translating arbitrary Qt applications.
- Tables, outline views, collection-view virtualization, rich text, drag and drop,
  modal sheets, multiple windows, and full document-application support.
- General deployment/signing automation or a new package/repository split.
- Changes to lifecycle semantics or fixes to other rendering backends.

## Existing Integration Boundaries

Use these current implementations as the reference, not archived design status:

| Boundary | Existing source | AppKit responsibility |
| --- | --- | --- |
| Element tree | [api.py](../src/pyrolyze/api.py) | Consume `UIElement` and existing mount/advertisement objects. |
| Native descriptors | [model.py](../src/pyrolyze/backends/model.py) | Supply ordinary `UiWidgetSpec`, property, event, and mount-point facts. |
| Reconciliation | [mountable_engine.py](../src/pyrolyze/backends/mountable_engine.py) | Reuse identity matching, changed-property application, child routing, and replacement. |
| Toolkit adaptation | [PySide6 engine](../src/pyrolyze/backends/pyside6/engine.py) | Implement AppKit construction, event, placement, and disposal details. |
| Window host | [native PySide6 host](../src/pyrolyze/pyrolyze_native_pyside6.py) | Add an AppKit host without copying toolkit-specific QWidget assumptions. |
| Lazy definitions | [grouped loading plan](LazyNativeBackendLoadingImplementationPlan.md) | Reuse accepted bounded groups, manifest lookup, signatures, and offline generation. |
| Portable facade | [unified factory](../src/pyrolyze/unified/factory.py) | Later map supported common operations to AppKit native nodes. |

Engine reuse is the intended design, not yet demonstrated AppKit compatibility.
Slice A1 proves the relevant seams before widening the catalog.

Keep three surfaces separate:

1. Author-facing: a single `AppKitUiLibrary` native callable surface, with
   explicit signatures and mount selectors following the existing native
   library pattern. Do not add a parallel set of convenience callables for
   the same native element.
2. Registration: descriptors and the small lazy index under
   `pyrolyze.backends.appkit`, inspected by existing compilation/mount machinery.
3. Runtime-only: host, constructor normalization, event bridges, placement,
   constraint ownership, and disposal helpers. These are not reactive UI calls.

The provisional stable native import is
`pyrolyze.backends.appkit.generated_library.AppKitUiLibrary`. Final author names
and property signatures are fixed by A1's manifest, before fixture source is
written. Use public Pyrolyze source forms, never hand-written compiler internals.

## Class Counts

PyObjC already supplies the language bindings. There are **zero new AppKit
language-binding classes** to implement; Pyrolyze still needs its catalog and
the appropriate construction, property, event, and attachment definitions.

### Full Public Class Inventory

Measured against the installed SDK's public AppKit headers:

| Count | Meaning |
| --- | --- |
| **316** | Distinct publicly declared AppKit classes, including supporting objects and controllers |
| **316** | Those classes available through PyObjC in the measured runtime |
| **55** | Classes in the `NSView` inheritance family, including the base class |
| **6** | Classes in the `NSWindow` inheritance family, including the base class |

The measurement used macOS 26.4 SDK headers, a macOS 26.6.2 runtime, Python
3.12.12, and PyObjC 12.2.2. It ran in an isolated temporary dependency environment,
without installing PyObjC into the shared project environment or creating UI
instances.

Counting method: read public `AppKit.framework/Headers/*.h` beneath the SDK
located by `xcrun --show-sdk-path`; strip comments; collect unique `@interface`
class declarations with a superclass, including Objective-C generic declarations;
exclude categories, protocols, forward declarations, and duplicate declarations.
Resolve each resulting class name through `AppKit` and verify it is an
`objc.objc_class`. The parser left no interface declaration unclassified, and
all 316 class names resolved. View/window family counts follow declared
superclass chains.

**316 is the inventory for complete public AppKit class coverage on this SDK.**
It is not 316 independently designed widget wrappers: many entries are data,
controller, layout, drawing, or service classes. Nor are the 61 view/window
classes the entire UI surface; menus, toolbar items, and other attachable objects
belong to separate families. A catalog record does not imply a class is directly
constructible or a valid mounted node.

A1 must turn this full inventory into an explicit classification manifest:
mounted node, host/infrastructure, supporting object, or unavailable/unsupported
with a recorded reason. Private runtime classes and Foundation category targets
are not added just because Objective-C runtime enumeration can see them. Future
SDK versions can change the total; this is a measured baseline, not an invariant
count for every macOS release. The five/twenty-class rollout does not redefine
the requested full inventory.

### Initial Milestone

| Native class | Role | How it enters the backend |
| --- | --- | --- |
| `NSWindow` | Native window and content-view ownership | Host-owned initially, not an engine-mounted window node. |
| `NSView` | Plain container/root view | Native descriptor and placement support. |
| `NSStackView` | Horizontal and vertical layout | One native class with different layout configuration. |
| `NSButton` | Push button and toggle | One native class with different control configuration. |
| `NSTextField` | Label and editable single-line text | One native class with different editing configuration. |

**Five distinct UI classes**, comprising **four engine-mounted class targets
and one host-owned window target**. They cover eight useful roles: window, view,
row, column, push button, toggle, label, and text entry. Roles are not necessarily
different native kinds or Python wrapper classes.

`NSApplication` is a sixth AppKit class used by host infrastructure, not a UI
node definition. Supporting objects such as delegates, notifications, and layout
constraints are additional implementation dependencies, not included in the UI
class count. This is not an estimate of the number of new Python source classes:
most control definitions should be data and generated wrappers, not bespoke
Python subclasses.

### Proposed Broader Starter Catalog

After the first milestone, these fifteen additional UI classes bring the
proposed starter catalog to **twenty distinct native UI classes**:

| Native class | Added capability |
| --- | --- |
| `NSSecureTextField` | Password entry |
| `NSTextView` | Multiline text |
| `NSScrollView` | Scrolling/document-view ownership |
| `NSSlider` | Range control |
| `NSStepper` | Numeric step control |
| `NSPopUpButton` | Discrete selection |
| `NSProgressIndicator` | Progress and busy indication |
| `NSTabView` | Tabbed content |
| `NSMenu` | Menu container |
| `NSMenuItem` | Menu entry and action |
| `NSToolbar` | Window toolbar |
| `NSToolbarItem` | Toolbar item |
| `NSSplitView` | Split-pane layout |
| `NSImageView` | Image display |
| `NSBox` | Grouping and separators |

This is a proposed expansion inventory, not a requirement to implement all twenty
in the first roll-build. Some common operations compose several native objects;
for example, numeric entry may use a text field and stepper. Menu/toolbar items
and tab content also need attachment contracts, not just property descriptors.
Helpers such as `NSTabViewItem` must be accounted for when those families are
designed; the twenty is not a complete supporting-object census.

A1 should make the full inventory reproducible with an offline tool and record
actual availability and inherited APIs for the selected implementation targets
using the chosen macOS/Python/PyObjC combination. Broad introspection belongs in
that tool, never ordinary import or first use. Do not count Foundation reexports
or private implementation classes as required UI definitions.

## Native Application Contract

### Main Thread And Event Loop

All native object construction, UI property access, attachment, disposal, and
event delivery run on the AppKit main thread. The initial application also runs
reactive evaluation there; introducing worker-thread rendering is unnecessary.

The host owns or joins one application event loop. Joining an existing AppKit
application must not start another loop or terminate an application owned by
somebody else. Closing this backend's window releases this backend's resources;
it does not introduce a generic lifecycle `close()` protocol.

Provide synchronous main-thread reconciliation with ordinary exception
propagation. If an off-thread submission entry is included, it queues a batch
to the main thread and returns a completion result, not a mounted node before
the work has executed. PyObjC's `AppHelper.callAfter` can perform the dispatch;
the exact completion carrier is fixed in A1. No claim of whole-runtime thread
safety follows from supporting this adapter-level entry.

Preserve submission order; do not silently coalesce arbitrary updates. Treat
submitted element data as fixed until completion. `UIElement` is a frozen
wrapper, but its property dictionaries and values are not transitively immutable.
The initial contract prohibits mutation after handoff rather than deep-copying
callbacks, resources, or native objects. Queued work reaching a closed host must
complete with an explicit closed-host error and perform no native mutations.

The existing accepted render-to-host boundary remains authoritative. This
backend does not make unpublished lifecycle candidates visible or invent an
atomic rollback guarantee for a partially applied native update. An application
failure must remain observable; repair/rebuild behavior after a native apply
failure must be specified in A1 rather than silently hiding the failure.

### Construction And Properties

Start with public PyObjC classes and explicit descriptors. Ordinary property
updates can use existing method accessors with Objective-C selectors translated
to Python method names. Do not add a new shared accessor enum merely to name
AppKit.

The engine currently resolves `mounted_type_name` to a Python type and calls it
with constructor arguments. PyObjC supports direct class construction, but its
initializer-derived keyword arguments have ordering rules. A1 must prove
`isinstance(native_class, type)` admission and constructor order/default behavior
for each initial class. If a local AppKit engine override is needed for designated
initializers, keep it in that backend and preserve the native instance as the
mounted object. Do not introduce one bespoke wrapper class per control by default.

Record which properties are mutable, create-only/remounting, or readonly. Preserve
empty strings, zero, and false values; omission is not the same as an explicit
empty value. Retained updates must compare against native editing state where
the existing property contract requires it, not only the previous element.

### Layout And Attachment

Initially the host owns one `NSWindow` and mounts exactly one view root into its
content area. The root fills the resizable window using backend-owned constraints
or an explicit equivalent; children in stack containers use native layout.
Arbitrary multi-child plain-view positioning is excluded until its layout
contract is defined. Do not mistake a plain container for a portable layout API.

Each mount-point descriptor must state allowed children, ordering, attachment,
detachment, and the chosen mutation policy. A stack removal must remove the
child from both arrangement and visible hierarchy when it is no longer mounted:
`removeArrangedSubview_` alone does not fully detach a view.

Reorder retained native children without recreating them. Capture and restore
the actual parent, sibling position, arrangement, and backend-owned constraints
when replacement requires placement recovery. Own and remove only constraints
created by this backend, not unrelated application constraints.

Exercise retain, move, insert, remove, replace, and failure as distinct outcomes.
Correct logical child order is not proof of correct native placement. Include
a retained nested stack followed by a trailing label to expose position drift.

### Events And Ownership

Use target/action for applicable controls and delegate/notification mechanisms
for editing. Map payloads explicitly into the existing event specification
contract. Replacement callbacks must take effect without repeatedly connecting
the same native signal/observer. Text change is not the same as editing finished.

The host/engine strongly owns mounted nodes and their connection records for
exactly their supported lifetime. Native target/delegate retention must be
checked per API rather than assumed. Backend bridge objects should refer weakly
to their dispatch owner and must not create a native-object/closure/engine cycle.

In particular, the existing `_event_dispatcher` closure captures the engine and
mountable. Do not simply retain that closure in an engine-owned native target.
A backend-local bridge can keep a weak engine reference and a connection token,
then resolve the currently registered callback at delivery. Account for removed
connections and object-identity reuse so a delayed callback cannot target a new
node. A1 must draw the ownership graph before selecting the final bridge shape.

Unmount/replacement/host shutdown removes observers, disconnects backend-owned
targets/delegates, releases connection records, and detaches views as applicable.
It must not erase target/delegate state owned by external code. Garbage collection
alone is not the event-disconnection contract.

Catch ordinary application callback failures at the Objective-C entry boundary
and report them through the host's explicit error path. Preserve render failure
semantics; do not report success or invoke another callback after an aborted
operation merely because the native boundary caught the exception. An error
reporter must not itself leak an exception back into Cocoa.

### Text Editing

Retain the text control while editing, and avoid writing its value when the
requested value already matches the current native value. Unrelated rerenders
must preserve focus, selection, caret, and marked/composing text. Explicit value
replacement, including clearing to an empty string, remains supported.

If a programmatic change arrives during composition, defer that text assignment
until composition ends rather than cancelling the user's input. A4 must specify
how a newer user edit supersedes a deferred assignment. Do not assert complete
input-method support until a visible native interaction has been exercised.

## Loading And Packaging

Keep the implementation in `pyrolyze` initially, following the existing backend
structure. Add a macOS-conditional optional dependency extra for the Cocoa
framework wrapper, not the umbrella package for every Apple framework. Record
the tested version range in A1; do not promise every Python/macOS combination
supported by PyObjC before testing it.

Ordinary Pyrolyze imports and another backend's selection must not import AppKit
or initialize `NSApplication`. The explicit AppKit runtime entry validates the
platform and dependency with an actionable error. Pure descriptor/source tests
remain runnable without a GUI or PyObjC; native tests require macOS and an
appropriate graphical session.

The native library uses the accepted lightweight facade/index and bounded
definition groups. If the current grouping API cannot express the curated AppKit
source, resolve that in A1 with its owner instead of introducing a competing
loader. No runtime full-framework scan and no eager all-widget definition module.
Track PyObjC's own import cost separately: sparse Pyrolyze definitions do not
prove that loading Apple's framework is free.

Suggested cohesive module ownership, subject to the A1 proof:

| Proposed path | Responsibility |
| --- | --- |
| `src/pyrolyze/backends/appkit/engine.py` | Adapter and native property/construction seams |
| `src/pyrolyze/backends/appkit/events.py` | Native targets/delegates, connections, error boundary |
| `src/pyrolyze/backends/appkit/placement.py` | View attachment and backend-owned constraints |
| `src/pyrolyze/backends/appkit/generated_library.py` | Stable author facade import |
| `src/pyrolyze/backends/appkit/_generated/` | Offline-generated bounded definition groups |
| `src/pyrolyze/pyrolyze_native_appkit.py` | Native host and event-loop ownership |
| `tests/appkit/` | Canonical fixture, native checks, and narrow mechanics |
| `examples/appkit_native_form.py` | Small working native demonstration |

Generated artifacts must enter the existing inventory/build admission machinery
if checked in. Do not edit generated shards as their own source of truth; provide
the curated manifest, deterministic generator command, and regeneration README.

## Implementation Slices

### A1 Compatibility And Manifest Proof

In the isolated checkout, install the optional dependency and record exact
Python, macOS, architecture, SDK, and PyObjC versions. Reproduce and classify the
full public class inventory, preserving the measured baseline above. Verify the
five initial class targets and supporting application objects. Produce the
constructor/property/event/mount manifest and the eight-role mapping, with
explicit source signatures.

Run a minimal native window/stack/button/text-field experiment against the shared
engine to prove construction, selector invocation, type acceptance, and mounting.
Prove the event ownership graph and determine whether the existing local hooks
or an AppKit-specific engine subclass suffice. Record root layout, native apply
failure recovery, and any off-thread completion contract.

Acceptance: concrete working bridge experiment and a reviewed seam map. Stop
before A2 if compiler/model changes, new semantic tags, or unsupported initializer
behavior require wider design. This experiment is not the final public API.

### A2 Native Host And Minimal Lazy Library

Add the optional dependency and platform boundary. Implement the host-owned
window and one-view-root contract, with view and stack definitions loaded through
the existing grouped library mechanism. Add the canonical compiled form fixture
with the public native source shape, initially using its containers.

Acceptance: one resizable native window, reusable root/stack identity, clean
host shutdown, no duplicate event loop, and unrelated backend imports remain
cold. If queued submission is included, prove ordered apply and closed-host
rejection with native operations running on the main thread.

### A3 Retained Placement And Disposal

Implement ordered stack attachment and native placement capture/restoration.
Extend the same fixture with insert/move/remove/replace and nested-stack updates.
Verify native hierarchy and arranged order, not just element order. Validate
constraint cleanup and ownership after repeated replacement.

Acceptance: retained child identities and positions are correct, removed views
leave the hierarchy, and no duplicate children or accumulated backend constraints
remain. Mutation counts and list-query counts must not grow quadratically for
unchanged lists or a single-child edit.

### A4 Controls And Callback Boundary

Add button/toggle and label/editable-text configurations using the two native
control classes. Implement target/action and editing callbacks, latest-handler
selection, error delivery, disconnection, and composition-aware text updates.

Acceptance: the canonical form supports click, toggle, typing, explicit clearing,
and unrelated rerenders without loss of control identity or editing state.
Removed/replaced controls cannot deliver callbacks into dead nodes. Callback
failure is observable and does not escape the native entry boundary.

### A5 Canonical Application And Measurements

Run the compiled fixture through the current accepted reactive runtime rather
than hand-building every update. Demonstrate counter changes, input changes,
conditional controls, reordered items, and the retained nested-stack case.
Evaluate retain/replace/remove/fail outcomes and verify no native update is
applied for a render result the existing runtime rejects.

Measure native framework import, Pyrolyze facade import, first requested group,
first window, retained-property update, one-child edit, and teardown separately.
Use fresh processes for import comparisons and warmed native sessions for
updates. Record counts and sizes at 10, 100, and 1,000 children where practical;
do not hide native layout cost inside Python reconciliation timings.

Acceptance: visible application evidence, reproducible measurements, focused
regressions, and an independently reviewed native ownership/placement contract.
No unmeasured speedup over Qt or browser engines is promised.

### A6 Distribution And First Milestone Acceptance

Verify the built package includes its descriptor inventory, generated groups,
signature metadata, and example instructions. Test installation with and without
the optional extra, native dependency errors, unsupported-platform behavior, and
ordinary imports without constructing application state. Document the supported
environment and remaining limitations.

Acceptance: the five-class milestone works from the packaged artifact, native
and source acceptance checks pass, and existing backend regression results are
recorded separately from pre-existing failures. This is the first release gate.

### A7 Optional Unified Facade And Catalog Expansion

Only after A6, decide which common operations deserve an AppKit mapping and
which of the fifteen expansion classes a real application requires. Keep the
existing abstract facade's unsupported operations explicit; do not advertise
a partial adapter as a fully supported backend. Do not change default backend
selection.

Expansion proceeds by bounded families with their own constructor, event,
attachment, ownership, and canonical interaction acceptance. Menu, toolbar,
scrolling, and tab support require separate plans/checkpoints before implementation.
Supporting-object counts and portable behavior limitations are updated then.
An unqualified implementation rollout of this draft ends at A6; A7 is a follow-up
decision, not automatic authorization to build the full twenty-class catalog.

## Verification And Review Gates

Use strict red/green/refactor for behavior changes. Prefer one canonical compiled
fixture for success-path behavior and snapshots of its descriptors/emitted source;
keep separate tests for narrow mechanics and failures only.

| Concern | Required check |
| --- | --- |
| Construction | Accepted constructor shapes/defaults and rejected unsupported initialization |
| Reconciliation | Retain, replace, remove, reorder, and failure outcomes |
| Placement | Native hierarchy/order including nested stack before trailing label |
| Properties | Omitted versus empty/false/zero and explicit text clearing |
| Events | Latest callback, no duplicate connection, disconnected/stale delivery |
| Text | Focus, caret/selection, composing input, and explicit programmatic replacement |
| Ownership | Repeated mount/unmount, observer removal, and native lifetime checks |
| Scheduling | Main-thread application; queue ordering/closed-host rejection if exposed |
| Loading | No AppKit on unrelated imports; only requested definition groups admitted |
| Packaging | Built artifact preserves facade, metadata, inventory, and optional dependency |
| Scaling | Operation counts across growing lists; time split into planning/apply/layout |

Native lifetime checks should account for autorelease pools and use native-aware
weak/lifetime observation where supported. A dead Python proxy alone does not
prove native release. Conversely, an observer left connected is a defect even
if a short memory check looks flat.

Before implementation, independently review the A1 boundary and the first
milestone scope. Review again after A4 for callbacks, text, and ownership, and
before A6 acceptance for packaged native behavior. A plan review is not runtime
acceptance. Each checkpoint records revision, environment, commands, results,
limitations, and unresolved obligations.

Expected test commands once the new tests exist, from the Pyrolyze repository:

```sh
uv run --with pytest --with pytest-cov pytest tests/appkit -q
uv run --with pytest --with pytest-cov pytest tests/test_mountable_engine_generic.py tests/test_mount_point_runtime.py tests/test_generated_backend_libraries.py -q
uv run --with pytest --with pytest-cov pytest -q
```

Source-only checks and real AppKit GUI checks must report separate results.
Missing dependencies/session capabilities may skip native checks in general CI,
but skips cannot satisfy the macOS acceptance gate. Do not report tests in this
draft as having run.

## Platform References

PyObjC exposes AppKit's C and Objective-C APIs, with documented exceptions;
ordinary native controls do not require new language bindings.
[AppKit wrapper notes](https://pyobjc.readthedocs.io/en/latest/apinotes/AppKit.html).

Direct Python class construction is supported with initializer-derived keyword
ordering requirements. Constructor compatibility still needs the engine proof.
[PyObjC instantiation](https://pyobjc.readthedocs.io/en/latest/notes/instantiating.html).

PyObjC provides main-thread dispatch and AppKit event-loop helpers.
[AppHelper](https://pyobjc.readthedocs.io/en/latest/api/module-PyObjCTools.AppHelper.html).
These do not imply that arbitrary Pyrolyze runtime execution is thread-safe.

Arrangement removal and visible view removal are different AppKit operations.
[Apple stack removal](https://developer.apple.com/documentation/appkit/nsstackview/removearrangedsubview(_:)).

Native target/delegate lifetime and exception boundaries require explicit care.
[PyObjC introduction](https://pyobjc.readthedocs.io/en/latest/core/intro.html),
[Cocoa exception handling](https://pyobjc.readthedocs.io/en/latest/notes/exceptions.html).

The bridge's platform support is broader than this backend's demonstrated
acceptance matrix. Record the actual environment rather than inheriting a blanket
compatibility claim.
[Supported platforms](https://pyobjc.readthedocs.io/en/latest/supported-platforms.html).
