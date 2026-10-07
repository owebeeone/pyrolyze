# Developer Documentation

Start here for current work. A plan is not proof that its implementation has
landed; use its status and the recorded acceptance scope.

## Lifecycle Integration

The current checkpoint is the accepted **library implementation** for lifecycle
completion evidence: L0-1 manager and L0-2 generated guards/hooks/goldens passed
Code/State GO/GO at lifecycle `4b86eec179942d96012aa4a1d92752a34cae87ef`.
Private owner adoption and historical probe transition are next. The SC2
field-only proof remains privately gated; resource routes are not activated.

[Resume handoff](YidlLifecycleIntegrationHandoff.md) records the repository
checkpoint, published compiler fixes, verification commands, and the next
bounded private-consumer step. It supplements, not replaces, the plans.

Read these documents in order:

| Document | Purpose |
| --- | --- |
| [Integration plan](PytoLifecyleIntegPlan.md) | Overall migration, remaining categories, and deletion obligations |
| [Single-cohort amendment](PytoLifecyleIntegSingleCohortPlan.md) | Current outer render ownership and exact supersession of earlier completion assumptions |
| [SC3 audit](PytoLifecyleIntegSC3.md) | Actual resource/writer routes and the gates before activation |
| [L0 completion contract](PytoLifecyleIntegSC3-L0Plan.md) | Next library implementation checkpoints and their verification |
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
