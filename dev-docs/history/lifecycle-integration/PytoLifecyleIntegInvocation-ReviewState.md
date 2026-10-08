# PytoLifecyleIntegInvocation - STATE-AXIS REVIEW

**Review object:** Bounded I3c leaf implementation, `0828f03..b188301216486aee3b43c1ecc7b7fe89307d0273`, governed by DRAFT `dev-docs/PytoLifecyleIntegInvocation.md` at the reviewed head.
**Baseline:**
- pyrolyze: `b188301216486aee3b43c1ecc7b7fe89307d0273`
- yidl-lifecycle: `05554397d1837ecbeafa36e4685477dd5ff30fc6`
- yidl: `a7cc1de7b630b55bd194940ecad83f3f1738cf8a`
- astichi: `1c47f781d3804130fdd61cbee07a3b2e4529158a`

**Date:** 2026-10-08
**Axis:** State transitions, authority fencing, failure and recovery. Independent, adversarial, read-only. Nothing here relies on the parallel reviewer. Filed verbatim by the lane owner.

**Verdict: GO** - No reproducible P0, P1, P2, or P3 findings within the bounded scope.

---

## 0. Evidence base

Repository object paths below are relative to their owning repository. Sources were inspected through `git show`, the complete bounded `git diff`, and tracked worktree reads.

- Read workspace/repository `AGENTS.md`, review-loop skill and report template.
- Checked controlling invocation document, single-cohort amendment's ownership/failure/publication clauses, and integration plan's I3c clauses through that amendment.
- Inspected `b188301:src/pyrolyze/runtime/context_state_lcm/leaf_slot_context.py:1-107`, facade argument readers, and surrounding attempt, local-pass, construction and managed-assignment machinery.
- Independently checked canonical invocation script, its JSON target, harness activation, and narrow normalization/replacement tests. Historical baselines were unchanged.
- Authorized native test command, with the prescribed environment and cache suppression: **23 passed in 10.46s** across the two permitted test files.
- Authorized ephemeral Python probes: **14 scenario variants passed**, covering preparation interruption, nested failure/reentry, callable-return token replacement, identity comparison and external-key admission.
- `git diff --check 0828f03 b188301216486aee3b43c1ecc7b7fe89307d0273`: passed.
- Start and final owning HEAD/status checks matched the exact tuple. Dependency trees were clean; pyrolyze retained only the two excluded untracked documents. Neither was read. No files or git state were modified.

## 2. Invariant analysis

- **Original authority remains captured.** Both entry points normalize inside the admitted attempt and recheck its owner immediately before assignment. Replacement during normalization was rejected without staging into or rolling back the replacement transaction.
- **Return-time authority loss fails closed.** Replacing the token inside the callable left the previously accepted positional/keyword pair intact and the replacement token active. Completion reported lost authority and refused reuse.
- **Failure is sticky across reentry.** A normalization callback that invoked a failing plain child and caught its exception could not rehabilitate the attempt through successful outer or later calls. Outer completion discarded candidates and preserved the first failure cause.
- **Local-entry rejection does not invent completion.** Caught duplicate native entry poisoned the attempt; cleanup released local activity, preserved accepted arguments, and allowed a fresh retry.
- **Recovery distinguishes discard from uncertainty.** Standalone preparation interruption restored candidate reads to accepted values and permitted retry. Missing original authority instead left completion uncertified and rejected retry.
- **Accepted/current and candidate remain separate.** Canonical observations correctly retain the prior pair through local success, parent failure and caught child failure. Fresh success publishes the new pair; identical invocations still execute.
- **The container contract remains shallow.** Publication did not invoke caller referent equality. Argument referents retain identity; no deep rollback or resource-lifetime guarantee is inferred.
- **Compatibility stays separate.** Unactivated calls retain sequential last-attempt tracking, including normalization failure. The private route does not use that adapter to restore managed state.
- **No new disk durability protocol exists in this diff.** Filesystem crash ordering and asynchronous rendering guarantees are not claimed by this checkpoint.

## 3. Risks and next action

Verification here is native, bounded and read-only. Full-suite and Python-assembly evidence remain lane-owner obligations; this report does not certify deferred resource routes, broader I3c migration or default activation.

Next action: file this State GO against the exact tuple for the lane-owner verdict merge. This verdict alone is not acceptance of the package.
