# Exact operator SFT6 to SFT24: independent training audit

Status: training phase terminal and independently audited; behavioral readout still pending. The
method was sealed postlaunch and after MAIN disclosed that checkpoint 7 existed, but before this
auditor read checkpoint contents. This is not a prelaunch registration.

## Result

The continuation is mechanically valid. All 18 fixed updates (Adam 7--24) form one continuous
checkpoint ancestry from exact SFT6. Every checkpoint contains 504 finite float32 Adam moment pairs
with the checkpoint's exact ordinal, a complete permutation of the same 72 trajectories, 324 root
turns, and 22,847 current-action target tokens. The total is 1,296 trajectory exposures, 5,832 root
turns, and 411,246 masked target-token exposures. The independent audit found no integrity errors.

The checkpoint-6 adapter was byte-equivalent at load; its six-step optimizer moments and Python,
Torch, and CUDA RNG states were restored, not reset. The child model was neither loaded nor called:
child outputs in these trajectories are retained historical context, including errors. The 504
parameter names were reconstructed from the pinned source model because names were not historically
logged; the mapping is source-derived rather than an original checkpoint field.

The pre-update, full-pass weighted teacher CE fell from 0.46536 at step 7 to 0.08875 at step 24.
First-producer NLL fell 0.96903 to 0.21020 and corrective NLL 0.38438 to 0.05913. On the separate
fixed 12-prefix diagnostic, post-checkpoint first-producer NLL fell from 0.96133 at SFT6 to 0.19485
at SFT24, and corrective NLL from 0.38998 to 0.05396. These measurements establish stronger teacher
fit only. They do not show that SFT24 freely acquires child outputs, accumulates live state, reduces
the requested scope, or answers correctly.

Checkpoint 24 was selected by the frozen rule, not by performance. Its adapter SHA-256 is
`94022838a64a530e1abc8daf6cd43502d8aec7d549b6bfec10dd4928b0ca9006`; its state SHA-256 is
`75b3138884cf526503bba311dae932158b7305a4958b478f73d286ad3a755171`.

## Time and next comparison

Optimizer plus checkpoint time was 3,658.48 seconds. The post6 and post24 diagnostic forwards took
10.50 and 10.05 seconds; total trainer time was 3,707.93 seconds and owner time 3,720.51 seconds.
These are separate from prior trajectory capture and the pending model-service readout.

The decision-relevant evidence is the already frozen paired readout: 48 full endpoints per policy
plus 12 first-action probes per policy. Strict nonzero successes, native availability, genuine child
acquisition, faithful returned-label use, width aggregation, scoped reduction, error recovery and
stopping will be reported separately. First-action probes are syntactic intent only; their programs
are not executed.
