---
title: Fresh-seed question-sensitive SFT semantic audit
status: complete_independent_audit
date: 2026-09-10
study: root-question-sensitive-seed-replication-v1
planned_endpoints: 144
observed_endpoints: 132
null_endpoints: 12
---

# Fresh-seed question-sensitive SFT semantic audit

## Result

The fixed six-update question-sensitive SFT policy again outperformed the
unchanged fixed24 policy on the same 72 exposed protected questions under fresh
paired rollout seeds: **51/72 versus 25/72 strict correct**, an operational
difference of +26. The qualified paired audit gives a +16 to +28 missing-data
bound; 60 pairs were jointly observed, with 22 gains, four losses, 20 both
correct, and 14 both wrong. Seven of eight reused context clusters had a
positive operational difference and one was tied. This supports sampling
robustness on this panel, not new-context or independent-training replication.

Manual review shows that most of the difference reflects better execution of
the requested computation rather than lucky scalar agreement. Among observed
endpoints, SFT6 executed the requested operator, scope, and threshold in
60/70 paths, versus 22/62 for unchanged. Grounded paths that both used observed
state and returned the strict host answer were **49/70 versus 15/62**. On the
planned denominator these are 49/72 versus 15/72; allowing every NULL to be a
grounded success gives a conservative difference range of +24 to +36.

The improvement is clearest on composed questions. SFT6 was faithful on 36/46
observed composed paths, with 31 grounded strict answers; unchanged was faithful
on only 3/39, all three grounded strict. Primitive paths were much less
separating: 24/24 faithful and 18 grounded strict for SFT6, versus 19/23 faithful
and 12 grounded strict for unchanged. This is evidence for learned root-side
operator/scope execution on this exposed task family, while not establishing
general operator competence.

## Child errors and coincidences

SFT6 had 11 faithful but wrong paths. For each, the trusted `qs_problem` oracle
applied *after manual fidelity judgment* to the actual observed child-label map
reproduced the returned final exactly. Thus these are upstream child-label
errors, not reduction errors. The unchanged policy had four analogous grounded
faithful wrong paths. The audit did not execute sampled model code and did not
repair any child labels.

Strict correctness alone still overstates execution. SFT6 had two unfaithful
strict coincidences: one filtered individual records by weight before user-level
thresholding, and one summed instead of taking a maximum. Unchanged had nine
unfaithful strict answers. Its index 92 sampled a correct count expression and a
lucky correct final, but overwrote the accumulated map, every reduction attempt
failed, and no observed scalar supported the final; it is faithful-plus-strict
syntactically but not a grounded faithful success.

The 70 observed SFT6 endpoints all completed acquisition and retained a full
16-record map. Among 62 observed unchanged endpoints, 59 completed acquisition,
two were partial, one attempted and failed, and 49 retained a complete map.
SFT6 used observed state in 65/70 finals versus 51/62 for unchanged. These are
manual dataflow judgments, not keyword matches.

## Availability and strict panels

The audit preserves all 144 planned slots. SFT6 has 70 observed and two NULL;
unchanged has 62 observed and ten NULL. One SFT6 and eight unchanged
authenticated empty finals are observed policy failures scored zero, not NULL.
The owner is `complete=false` because 135 RESULT files exist, but it reports no
runtime error, both service stages completed, and release is clean. The parent
exited 1 without timeout after 1,643.003 seconds and reported no GPU process.

Strict planned scores and bounds are:

| Stratum | SFT6 | Unchanged |
| --- | ---: | ---: |
| All 72 | 51, bound 51–53 | 25, bound 25–35 |
| Primitive 24 | 18, bound 18–18 | 13, bound 13–14 |
| Composed 48 | 33, bound 33–35 | 12, bound 12–21 |
| Zero-gold 26 | 24, bound 24–25 | 13, bound 13–16 |
| Nonzero 46 | 27, bound 27–28 | 12, bound 12–19 |

The zero-gold gain is reported separately because zero-compatible success need
not demonstrate computation. The nonzero strict difference and manual
faithfulness both favor SFT6.

## Native identity and physical cost

The qualified reader found no service-binding errors and authenticated all
available native rows against the frozen prompts, model bindings, token IDs,
and checkpoint files. The physical union contains 1,112 model attempts:
1,103 HTTP 200 and nine HTTP 400. Known usage is 2,781,759 input tokens,
123,255 output tokens, and 2,609,264 cached tokens; nine attempts have unknown
values for each usage field. Stage counts are 346 SFT6 and 766 unchanged
attempts. These are physical local-model records, not provider billing.

## Method and limits

The qualified native method predates execution. The exhaustive semantic review
was performed after outcomes existed: two reviewers manually read every actual
program and parent/toolid observation across the 144 planned rows, including
all authenticated empty finals. This author did not implement the study, but
previously contributed to audits of the original QS campaign. No model code was
re-executed and no heuristic classifier supplied the fidelity labels.

This is a fresh-seed replication on the same eight research-exposed contexts
and questions, using the same trained SFT6 and unchanged fixed24 checkpoints.
The trained policy ran first, reversing the original serial order, so order and
cache effects are not isolated. The evidence supports a stable panel-specific
root execution gain and motivates genuinely new tasks or contexts; it does not
show that child accuracy improved or that the learned routine generalizes.

Machine-readable per-row judgments, notes, qualified native evidence, subgroup
summaries, and source hashes are in `SEMANTICS.json`. The two segment files retain
the detailed manual counterexamples and faithful-child-error inventories.
