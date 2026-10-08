# Developer Documentation

Start here for current work. A plan is not proof that its implementation has
landed; use its status and the recorded acceptance scope.

## Lifecycle Integration

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
