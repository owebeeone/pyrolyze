# Developer Documentation

Start here for current work. A plan is not proof that its implementation has
landed; use its status and the recorded acceptance scope.

## Native Library Loading

The [lazy native backend loading plan](LazyNativeBackendLoadingPlan.md) passed
independent Consistency and Safety design review after one regeneration-recovery
correction. The [review checkpoint](LazyNativeBackendLoadingPlan-ReviewCheckpoint.md)
records the exact accepted revision, verdicts and remaining slice-0 proof gates.
This is design acceptance only: no lazy loader, compiler change or performance
improvement has been implemented by this checkpoint.

## Lifecycle Integration

Lifecycle-backed completion is now the default runtime selection, including the
enabled legacy boolean setting. See the current routing section of the
[adoption audit](PytoLifecyleIntegAdoptionAudit.md) for activation checks and the
remaining compatibility-retirement scope. Explicit legacy selectors and private
checkpoint helpers remain for their existing consumers; the staged rollout
summaries below are historical acceptance limits, not current default routing.

The [adoption audit](PytoLifecyleIntegAdoptionAudit.md) inventories remaining
holders and includes the active handwritten-lowering removal project. That
cleanup uses compiled fixtures and thin observers to prevent test/runtime drift.
The audit also records confirmed gates after I6b. Keyed-loop selection is committed and
container routing is committed behind a private gate. The
[pass-state checkpoint](PytoLifecyleIntegPassState.md) now implements managed
visitation and invalidation acknowledgment behind `_enable_pass_state_render`.
The compiled site-selection correction separates dirty lookup from clean
retention and null-selection removal; it is implemented and tested.
Aggregate review's caught-preparation failure boundary is corrected in `0f88db2`.
The adoption audit now records a real UI trial and the opt-in `lifecycle` selector
for automatic root completion. Small native UI interactions pass; normal-route
adoption remains blocked by the recorded consumer, rebinding, and scaling gaps.
The [override read acknowledgment note](PytoLifecyleIntegOverrideReadAcknowledgment.md)
records the bounded redundant-publication notification correction and its test
matrix; runtime implementation is now present on the opt-in candidate. The lightweight
[Safety draft review](PytoLifecyleIntegOverrideReadAcknowledgment-ReviewSafety.md)
reported GO with no findings on the hash-recorded draft. This is readiness for
bounded implementation, not runtime acceptance or default activation. Actual
verification is recorded in the adoption audit.

The [container routing checkpoint](PytoLifecyleIntegContainerRouting.md) classifies
supported compiled/native/directive scope calls before constructing their slots.
It is committed as `a87a7ac` and tested behind its own private gate.
Normal routing and arbitrary external context-manager admission are unchanged.

The [keyed-loop checkpoint](PytoLifecyleIntegKeyedLoops.md) now implements managed
item selection and original-owner iteration behind another proof gate. The
approved compiler execution scope distinguishes successful `break` from body
failure; normal routing and unrelated container admission remain unchanged.

Latest bounded work: [directive and completion queues](PytoLifecyleIntegCompletionQueues.md)
migrates directive selectors and captures render/expression callback batches
until accepted outer completion. It removes base class-name completion dispatch
without activating normal routing. Aggregate review and adoption remain pending.

The [override publication checkpoint](PytoLifecyleIntegOverrides.md) adds managed
lexical override selection and post-publication stream delivery behind its own
proof gate.

The [component selection checkpoint](PytoLifecyleIntegComponentSelection.md)
adds managed identity/schema/child selection and component replacement/retirement
under the single outer decision. Normal-route adoption remains gated.

Library completion evidence is accepted at lifecycle
`4b86eec179942d96012aa4a1d92752a34cae87ef`. The **private Pyrolyze consumer**
and historical probe transition are now accepted after Code/State GO/GO at
`b1461a1128da15c21dad482d41bd5792253904cd`; see the
[consumer checkpoint](PytoLifecyleIntegSC3-L0Consumer.md) for its exact tuple,
review reports, and verification. The SC2 field-only gate remains private;
other resource routes are not activated. The
[bounded callback-selection implementation](PytoLifecyleIntegCallbacks.md)
is accepted after Code/State GO/GO at
`6be1b8f610c13eda18a451688377370cb1dbb087`. It migrates selection stores and
callers and adds a separate private handler-enabled proof, not live holder
replacement. Bounded I3c invocation-value migration continues; other resource
categories and default-runtime activation remain gated.

The [bounded invocation checkpoint](PytoLifecyleIntegInvocation.md) accepts leaf
arguments after Code/State GO/GO at `b188301216486aee3b43c1ecc7b7fe89307d0273`
and records the legacy last-attempt compatibility adapter. Slot-call invocation
values plus plain-value binding selection are also accepted after Code/State
GO/GO at `050ec5bdfc36b434fd0ad4b32d99de50cc5352f0`, after one bounded correction.
Effects, external stores, and mount bindings remain gated on the new private
route; their existing runtime routes are unchanged. Remaining invocation/resource
categories continue through SC3/I4, not automatic activation or completion of
all I3c work.

The [subscription checkpoint](PytoLifecyleIntegSubscriptions.md) adds a separate
subscription-enabled proof. Its hybrid ownership is operator-approved: lifecycle
owns private Python-lifetime wrappers, while those wrappers retain/release the
explicitly reference-counted subscription resources. Value snapshots do not retain
ownership. The operator deferred separate review to the larger integration review;
the checkpoint is implemented/tested, not independently accepted. This does not activate normal
rendering, async effects, or mounts. Synchronous effects are admitted only by
the separate checkpoint below.

The [synchronous-effect checkpoint](PytoLifecyleIntegEffects.md) extends that
proof with inert candidate resources and post-publication setup. It preserves
stable-dependency reuse, cleanup-before-replacement, and no setup on rollback;
multiple pending requests select the latest callback. It is implemented/tested,
with separate review deferred to the aggregate integration review. Async
effects, mounts, and default-runtime activation remain gated.

The [async-effect checkpoint](PytoLifecyleIntegAsyncEffects.md) extends the proof
with cancellable operations, weak completion callbacks, and teardown fencing.
It reuses the synchronous delivery loop and private resource wrapper; shared
legacy handlers, mount admission, and normal routing remain unchanged.

The [mount checkpoint](PytoLifecyleIntegMounts.md) adds a separate native-container
and slot-call advertisement proof. Candidate surfaces validate before publication;
accepted surfaces derive from committed selections. Slot-expression collections,
opaque host context managers, structural directives, and normal routing are not
activated by this checkpoint.

The [call-site collection checkpoint](PytoLifecyleIntegCallSites.md) replaces
legacy lifecycle records with YIDL-owned collection storage and transient
visitation, preserving explicit binding ownership. The unused `replace_current()`
escape is removed. Expression binding completion and admission to the private
outer-render route remain separate work; this is not normal-route activation.

The [plain-expression checkpoint](PytoLifecyleIntegExpressions.md) now adds a
separate shared-render proof: detached value selection and visitation pruning
publish/discard only with the outer owner. Standalone completion is retained;
resource-bearing expressions remain excluded pending their adapters.

The [subscription-expression checkpoint](PytoLifecyleIntegExpressionSubscriptions.md)
adds a separate proof with detached refresh snapshots and explicit resource
ownership through lifecycle-owned collections. Effect/async/mount expressions
and normal-route activation remain gated; aggregate implementation review is
still deferred.

The [synchronous-effect expression checkpoint](PytoLifecyleIntegExpressionEffects.md)
adds inert candidate effects and post-publication delivery after collection
retirement. Async-effect/mount expressions and normal-route activation remain
gated, with aggregate review still deferred.

The [async-effect expression checkpoint](PytoLifecyleIntegExpressionAsyncEffects.md)
reuses the same ownership/delivery path with stable weak notification hosts,
cancellation, and callback fencing. Mount expressions and normal-route adoption
remain pending; aggregate review is still deferred.

The [mount-expression checkpoint](PytoLifecyleIntegExpressionMounts.md) adds
candidate surface validation and committed UI anchors for expression selections.
The resource-expression adapters are implemented behind their proof gates;
remaining graph/registration work, aggregate review, and normal adoption continue.

[Resume handoff](YidlLifecycleIntegrationHandoff.md) records the repository
checkpoint, published compiler fixes, verification commands, and the next
bounded integration steps. It supplements, not replaces, the plans.

Read these documents in order:

| Document | Purpose |
| --- | --- |
| [Integration plan](PytoLifecyleIntegPlan.md) | Overall migration, remaining categories, and deletion obligations |
| [Single-cohort amendment](PytoLifecyleIntegSingleCohortPlan.md) | Current outer render ownership and exact supersession of earlier completion assumptions |
| [SC3 audit](PytoLifecyleIntegSC3.md) | Actual resource/writer routes and the gates before activation |
| [L0 completion contract](PytoLifecyleIntegSC3-L0Plan.md) | Accepted library/consumer contract and verification boundaries |
| [Private consumer acceptance](PytoLifecyleIntegSC3-L0Consumer.md) | Exact accepted tuple, review closures, and next adapter gate |
| [Callback selection](PytoLifecyleIntegCallbacks.md) | Bounded implementation contract, verification, and implementation-review status |
| [Invocation values](PytoLifecyleIntegInvocation.md) | Accepted leaf/plain-value slot-call migrations, completion-adapter meaning, and remaining invocation/resource gates |
| [Subscription completion](PytoLifecyleIntegSubscriptions.md) | Tested subscription proof, private-wrapper ownership rationale, cleanup timeline, and deferred aggregate-review obligation |
| [Synchronous effects](PytoLifecyleIntegEffects.md) | Tested effect proof, post-publication delivery, cleanup/failure behavior, and deferred aggregate-review obligation |
| [Async effects](PytoLifecyleIntegAsyncEffects.md) | Async proof, cancellation/cleanup, weak callbacks, and remaining activation gates |
| [Mount advertisements](PytoLifecyleIntegMounts.md) | Detached selection, native-container shape, candidate validation, and committed surfaces |
| [I3a field migration detail](PytoLifecyleIntegI3aPlan.md) | Remaining common-field migration; read through the single-cohort amendment |

Closed checkpoint evidence and review campaigns are in
[history/lifecycle-integration](history/README.md). Those records preserve
earlier revisions and acceptance limits; they do not override the current
amendments or certify later implementation.

## Standing Rules

- [API design](ApiDesignRules.md)
- [Semantic UI design](SemanticUiLibraryDesignRules.md)
- [Package structure](PackageStructureRules.md)
- [Repository instructions](../AGENTS.md)

## Other Work

Other subsystem documents remain in place where completion or supersession has
not been established. In particular, the mount/surface, backend, widget, and
developer-tool work is not declared complete by this cleanup.

- [Mount/surface placement](mount-surface-placement/HostSurfacePlacementDesign.md)
- [Mount/style expansion](mount-style-expansion/ContainerStyleGeneratorDesign.md)
- [Widget reconciliation](widget-reconcile/README.md)
- [Developer-documentation tool](active/dev-docs-tool/README.md)
- [Unified native API](UnifiedMountBasedNativeApi.md)

## Maintenance

Keep current contracts and unfinished plans discoverable here. Move completed
plans, superseded designs, review prompts/reports, and checkpoint evidence into
`history/`, grouped by subject. Preserve historical evidence and repair current
links; do not rewrite an old verdict or silently change its pinned revision.

Archiving a document does not cancel an unfulfilled implementation obligation.
Record that obligation in the current plan before moving its original proposal.
