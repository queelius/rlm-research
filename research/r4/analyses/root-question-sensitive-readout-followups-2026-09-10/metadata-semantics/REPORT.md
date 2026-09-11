---
title: Metadata-shift question-sensitive SFT semantic audit
status: complete_independent_retrospective
date: 2026-09-10
study: root-question-sensitive-metadata-transfer-v1
planned_endpoints: 144
observed_endpoints: 127
null_endpoints: 17
---

# Metadata-shift question-sensitive SFT semantic audit

## Result

On the same eight research-exposed contexts, after replacing user names,
weights, and thresholds, the fixed six-update question-sensitive SFT policy
was strictly correct on **53/72** planned endpoints versus **17/72** for the
unchanged fixed24 policy. All 72 SFT6 endpoints were observed; only 55/72
unchanged endpoints had an authenticated native final. Treating every NULL in
the most adverse direction gives a strict difference bound of **+19 to +36**.
The operational difference was positive in all eight context clusters.

Manual review supports a substantive execution difference, not merely scalar
agreement. SFT6 actually executed the requested operator, scope, and threshold
over its returned child-label map and used the resulting scalar in **62/72**
paths; unchanged did so in **17/72**. The corresponding grounded strict counts
were **50/72 versus 12/72**. On the 55 jointly observed pairs, requested
computation changed from absent to present in 33, remained present in 17, and
remained absent in five; no jointly observed pair lost it.

This is evidence that the learned root routine transfers across this joint
metadata change on an exposed task family. It is not new-context evidence, an
independent training replication, or proof of generic operator competence.

## Composition, errors, and coincidences

For the 48 composed questions, SFT6 performed the requested computation in
38 paths and was both performed and strict in 32; unchanged performed none.
For the 24 primitive questions, the corresponding counts were 24/24 and 18/24
for SFT6, versus 17/24 and 12/24 for unchanged.

Strict correctness still overstates semantic execution. Three correct SFT6
answers were unfaithful coincidences (indices 15, 35, and 38): literal recovery
after errors, a string-versus-integer comparison producing zero, and a
record-count computation in place of the requested user-level threshold.
Unchanged had five strict-but-unperformed coincidences (75, 78, 99, 107, 136),
including sum-for-maximum and missing-condition substitutions.

SFT6 also had 12 faithful but wrong finals. In every case, applying the trusted
task oracle to the *actual returned label map* reproduced the displayed scalar,
so the error is explained by upstream child labels rather than root reduction.
The five faithful-but-wrong unchanged paths have the same property. No gold
labels were substituted, and no sampled model code was reexecuted.

Operator-level performance remains uneven. SFT6 performed 8/8 count, 8/8
distinct-user, and 8/8 weight-sum questions, but only 11/16 conditional-weight,
13/16 maximum, and 14/16 threshold questions. Thus the result supports broad
transfer within this panel while retaining concrete execution failures.

## Availability, pairing, and zero support

All 144 planned slots remain in the denominator. SFT6 has 72 observed, zero
NULL, and zero authenticated-empty endpoints. Unchanged has 55 observed, 17
true NULL, and 11 authenticated empty finals; the empty finals are observed
policy failures scored zero, not NULLs.

Across all 72 operational pairs, strict outcomes were 37 gains, one loss, 16
both correct, and 18 both wrong, where a NULL necessarily contributes no
success. Restricting to the 55 jointly observed pairs gives 25 gains, one loss,
16 both correct, and 13 both wrong. These are endpoint counts clustered within
eight contexts, not 72 independent experimental units.

Zero-gold questions are reported separately: SFT6 was strict on 27/28 and
performed-and-strict on 25/28, versus 8/28 and 5/28 for unchanged. On nonzero
questions the corresponding figures were 26/44 and 25/44 versus 9/44 and 7/44.
The nonzero result and manual execution audit show that the gain is not solely
a best-constant or zero-answer shift.

## Native evidence, lifecycle, and cost

The qualified native reader reported no binding errors. It authenticated model,
prompt, token, branch, tool-call, observation, and final correspondence for the
127 available endpoints. The owner recorded both service stages work-complete,
clean release, no active service, and no internal error, but `complete=false`
because only 127 RESULT files exist. The parent exited 1 without timeout after
1,907.990 seconds; this operational status does not convert missing finals into
zeros.

The physical union contains 1,537 model requests: 1,521 returned native
completions and 16 failed or unconfirmed completions (all recorded HTTP 400).
Known usage is 4,022,871 input tokens, 135,514 output tokens, and 3,836,816
cached tokens; each field is unknown for 16 attempts. Stage attribution is 300
SFT6 and 1,237 unchanged requests. These are physical local-model records, not
provider billing.

## Method and limits

This semantic audit is retrospective and aggregate-aware: MAIN supplied strict
and availability totals before manual path review. The reviewer contributed to
earlier QS audits but did not author this metadata follow-up. Every available
program and its parent/tool-linked observations was read manually. A sampled
correct expression counted only if it executed successfully, its scalar was
grounded in an actual returned map, and the final used that scalar. The trusted
oracle was used only after that judgment to diagnose child-label errors.

The intervention jointly changes names (`u0..u3` to `u4..u7`), record weights
(to 8–15), and thresholds (to 13/25), while retaining texts, record IDs,
operators, and eight exposed contexts. It therefore tests transfer of the
trained routine across a metadata package; it does not isolate which metadata
field matters. The 16 count/distinct questions change names only, whereas 56
questions also depend on new weights or thresholds. A component factorial or
genuinely new task family is the appropriate next discrimination.

`SEMANTICS_V2.json` is authoritative. The unsealed `SEMANTICS.json` is an
incomplete intermediate draft that omitted the gold field needed for final
stratification; it is retained for audit history and is not used here.
