# Lazy Native Backend Loading Plan: Remediation 1

Status: proposed correction; reviewer closure pending.

Round 1 reviewed `4f0812802d2abd951e46fb72995a66f9c94d45bb`.
Consistency reported GO with no findings. Safety reported NO-GO with one P2.
There was no blind convergence because only Safety found a blocking defect.

| Finding | Disposition | Closure evidence |
| --- | --- | --- |
| Safety P2-1: interrupted multi-file regeneration admits an unrecoverable mixture | Accept. Apply the operator's whole-directory staging proposal: place all generated artifacts under one replaceable root, require successful generation plus complete validation, retain the old directory during two-rename offline promotion, restore before retry, and gate packaging on complete output with no pending promotion. | Revised design must cover interruption at each directory rename and marker transition, failed generator exit, first generation and backup cleanup; future tests recover complete old or new output, preserve unrelated files, and verify fresh-process lookup and packaging. Safety must retrace the original partial-replacement counterexample. |

One document patch closes the finding; no generator or runtime is implemented.
The publication mutation boundary becomes explicit, so fresh Consistency and
Safety reviewers replace the original pair for round 2. The new Safety reviewer
inherits the original finding and must verify its original counterexample.
Both review prompts require changed-range analysis. The operator's bounded
remediation limit remains in force.
