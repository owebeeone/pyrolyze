# Callback Selection Remediation 1

Reviewed candidate: Pyrolyze `e1cce818e3c99712d54b37976a5794a8d85cfb57`.
Code and State returned NO-GO. One shared omission root converged independently;
the other findings are distinct. This is one bounded compatibility/safety patch,
not a new design review or expansion of admitted resources. Dependencies stay
unchanged. The same reviewers recheck their original counterexamples.

| Finding | Disposition | Closure Evidence |
| --- | --- | --- |
| Code P2-1 | Correct the retained unactivated component failure route: explicitly discard only its provisional selection using generated managed setters, not manual current-value application. The private outer route still discards through its owner. | New canonical owned-handler reference comparison: caught child failure, parent success, accepted A retained, then successful B replacement; original/monolithic/decomposed agree. |
| Code P2-2; State P2-1 | Track which component-owned argument passes participated in this attempt. Restrict omission normalization to them and reset their visitation/order scratch after coherent publication/discard under existing cleanup fencing. | Extend the owned-handler golden: failed omission followed by child-only rerun, unrelated out-of-pass handler removal, and retained component reuse without invocation all preserve A; later successful parent omission retires it. |
| Code P2-3 | Treat pending explicit retirement as a selection-reset condition. Reselection cancels it even when equal to current; ordinary A/B/A eligibility remains unchanged. | Canonical successful/failed deactivate-reselect for identical and value-equal callbacks with dirty=False, preserving current visibility and stable dispatch. |
| State P2-2 | Capture the original owner/token, evaluate callback properties/equality fully, then recheck that same authority immediately before writes. Never borrow a replacement token or a new owner. | Narrow equality/property-access replacement faults on both backends: replacement has neither pending field, accepted callback unchanged, original attempt quarantined. |

The unactivated failure correction is a temporary local-discard compatibility
adapter, not a restored commit_handler/rollback_handler transfer engine. Lifecycle
still prepares/applies/discards physical storage. Retiring that adapter follows
completion ownership migration; it does not change the parent-catch contract
of an unactivated route in this checkpoint.

Run red cases first, then affected canonical/fault coverage on both assembly
backends, the focused native suite, full default, and the same broader comparison.
Settle one revised commit. Re-verdicts are restricted to finding closures and
the changed range; at most two remediation rounds, no third reviewer.
