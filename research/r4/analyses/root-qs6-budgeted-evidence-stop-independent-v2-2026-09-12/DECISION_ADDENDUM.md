---
title: Budgeted evidence screen mechanism decision
date: 2026-09-12
status: completed_cpu_addendum_no_gpu_admission
---

# The selector reduced logical label access but did not reduce real compute

The raw causal-trace audit recovers information hidden by the inherited exporter’s
`first prompt/model mismatch` failure. Eager has 6 strict finals, 5 consistent with
the accepted `finish()` state, and 4 exact against both host gold and the actually
supplied saved map. Budgeted has 5 strict finals, 4 finish-consistent, and 3 exact
against both targets. There are only three jointly gradeable pairs: one budgeted
win and two ties; 21/24 pairs remain unknown. This is not accuracy evidence for a
better selector.

The four correct eager episodes each acquired all 16 labels. Budgeted produced one
correct finish after acquiring 12 labels and two correct zero-request finishes on
questions whose answer was zero. Thus there is one concrete faithful-consistency
example of partial acquisition (12 rather than 16), but no broad evidence that the
model learned to stop from a sufficient subset. Another consistent zero-request
budgeted finish is wrong, so zero requests alone is not successful early stopping.

Across all episodes, accepted callback access fell from 80 to 28 label IDs (−65%).
These are **logical accesses to saved helper-map values**: both arms made zero
actual child-model calls and have no child tokens or log probabilities. Meanwhile
budgeted used 90 rather than 74 physical root calls (+21.6%), 285,006 rather than
196,835 root input tokens (+44.8%), and 46,839 rather than 38,824 root output tokens
(+20.6%). It is therefore slower/more expensive in the measured root path despite
fewer logical labels. Unknown usage remains nonzero for two budgeted coordinates.

Interface/working-state failure dominates. Eager recorded 21 rejected API actions
and budgeted 22. Only 6 budgeted `finish()` calls were accepted; two lack complete
finalize/audit state, and only 5 causal strict finals survive. Most rows make no
accepted classification request and never produce a strict final. The current API
returns each accepted mapping but does not render a cumulative, canonical state in
later observations. The root must reconstruct acquired IDs, returned labels,
remaining IDs, and rejected calls from conversation history.

## Smallest warranted follow-up

The checkable-working-state idea is supported as a mechanism test, not as a deeper
recursion claim. Compare the current budgeted arm against the identical budgeted
action set with one neutral host-rendered ledger after every API action:

- accepted/rejected action and reason;
- acquired `(id, returned saved-label)` pairs in canonical source order;
- remaining record IDs and calls remaining;
- finished flag and, only after `finish`, the model-declared answer/evidence IDs.

Do not include host gold, an operator, a subset recommendation, or a computed
answer. Preserve wrong saved labels. Use fresh paired seeds on the same 24 frozen
tasks, the same weights, four-call/16-ID limits, and the same total root turn and
generation caps. Charge ledger input tokens normally. This tests the net value of
checkable state under a larger input footprint; it does not isolate ledger content
from extra prompt tokens and does not test child speedup.

Primary mechanism readout: consistent strict finals and rejected-action counts.
Secondary readouts: host/supplied-map exactness, accepted unique IDs, duplicate or
unknown requests, and physical root calls/input/output tokens. Retire the ledger
direction if it does not materially improve protocol completion or merely produces
more wrong early finishes. Only after a completion signal should it be tested on a
new context group or compared with a fresh-root handoff.

## Frozen sources

- Independent result SHA256: `82b2151159182321e55595f2cd6359c420b7d443f8490d96a6815d7beaedf438`
- Independent report SHA256: `f4388205b37c1e6aad079b64aeb7ac515ada414a10057b6bde59050fa6062058`
- Owner terminal SHA256: `6272598acd70cc02d46639c40f847e0e499dfabc6bbb07beb7ccb6526a03477c`
- Eager counts SHA256: `fd49ee9b52ec750bd14c240d85905cd2d77efd47e2da2b6d887f0992135b8802`
- Budgeted counts SHA256: `e8265f348b1116debb8ecaf4efa4eb7a087023bc17da7f99033b86324ac53265`

