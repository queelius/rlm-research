---
date: 2026-09-10
status: ready_for_main_review_not_accepted
scope: independent CPU-only prelaunch review
---

# Stable-anchor192 independent review

The first sealed revision had one material scoring defect: an unavailable late-position score was
substituted with zero in paired gains even though promotion allowed 15/16 available calls per cell.
This could make a missing labels-only baseline look like treatment gain or make a missing keyed call
look like treatment loss. The original scoring source and READY are preserved under
`superseded/2026-09-10-null-bounds/`, with an additive source map.

The amended scorer reports a paired-known estimate and worst/best missing-outcome bounds over the
fixed 1,536-label planned denominator. These are identification bounds, not confidence intervals.
Promotion requires the lower bound to clear the 25-point treatment gain threshold, the lower bound
of the direct treatment-minus-sequential contrast to be at least -10 points, at least 12 context
lower bounds above zero, at least 15 available calls per cell, and no contract or availability
disadvantage. Direct contrasts cancel a shared missing labels-only baseline. Focused missing-baseline,
missing-treatment, and all-NULL fixtures pass.

The 13 frozen scientific inputs are byte-identical to the superseded READY closure. Independent
reconstruction matched all 192 plans and request bodies, with one call in every context-by-arm cell,
the same per-context seed across its 12 arms, no host gold in request bodies, and 192/192 canonical
gold completions mapping to 48/48 under the declared scorer. Native authentication rejects unknown
finish branches and verifies prompt and completion token identity. The collector retains all 192
planned rows, including undispatched and invalid outcomes, and separately reports physical attempts
and unknown usage.

The owner is bounded to one explicitly assigned GPU: 1,800 seconds outer, 1,770 seconds owned,
1,650 seconds work, four workers, and 90 seconds per request, with a release path in `finally`.
`complete` means the collector completed and the service released; it does not mean all 192 outcomes
were observed. Post-terminal reporting must preserve that distinction and use the bounds when NULLs
occur.

No further experiment-compromising defect was found in the frozen request binding, score-to-record
mapping, paired layout, native transport, or owner lifecycle. This is an independent readiness
finding only; MAIN has not accepted the amended producer and no GPU launch is authorized by it.

Interpretation remains limited. Structured decoding forces the key-bearing grammar and may supply
key continuations; output order is also fixed to displayed order. Therefore the experiment compares
encoding packages and can distinguish stable-key benefit from sequential numbering, but cannot by
itself establish a binding, copying, or counting mechanism. The 16 newly selected MNLI contexts
exclude all named prior research inventories, but use a familiar task/model and are not guaranteed
pretraining-unseen. They are the independent paired units; records and labels within them are
dependent.
