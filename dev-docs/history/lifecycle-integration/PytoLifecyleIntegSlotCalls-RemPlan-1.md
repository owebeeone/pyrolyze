# Slot-Call Value Adapter Remediation

Date: 2026-10-08. Reviewed Pyrolyze checkpoint:
`337bdb7fdbc578f056ca6f2bfd4a20caa6391665`; dependencies unchanged from the
invocation checkpoint. Both peer-blind reviewers found the same root cause.
Acceptance remains blocked until originating reviewers verify the correction.

| Finding | Disposition | Closure |
| --- | --- | --- |
| Code P2-1 and State P2-1: admission discards its selected handler and binding classifies again | One bounded correction: return the approved plain-value handler from private admission and bind through that exact handler. Do not reclassify or change shared legacy dispatch. | Stateful `__class__` recognition reproducer on native/Python; successful publication and parent-failure discard must invoke no external resource callbacks. Original accepted binding survives failure; ordinary rejection permits clean retry. |

Keep private binding detachment, one-record publication, and existing ownership
fencing unchanged. No resource activation, shared handler/core API change,
compiler/library edits, or adjacent redesign. File verbatim re-verdicts on the
revised settled tuple. The passing first-round matrix does not waive the defect.
