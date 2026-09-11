---
title: Supplied-plan scale ceiling is limited by child label errors
date: 2026-09-10
status: complete_native_audit
study: root-lambda-supplied-plan-ceiling-v1
---

# Question and answer

If the experimenter supplies complete 32-record acquisition blocks and a deterministic public
J1 reducer, can the fixed c32 child produce the exact scale-task answer?

Not on these eight frozen episodes: **0/8 exact**, with no NULLs. All 40 child calls were
natively authenticated, and every episode had a complete valid predicted label map. Running
the same public reducer on private oracle labels reproduced host gold in all 8/8 episodes.
Thus the supplied acquisition and reduction plan is sufficient with correct labels, while
the fixed child's remaining classification errors are sufficient to prevent every exact
scalar here.

# Decomposition

The child classified 1,129/1,280 records correctly (88.20%). The deterministic reducer still
missed by absolute errors `[1, 16, 7, 22, 6, 8, 15, 42]`, totaling 117. At size 64, label
accuracy was 223/256 and total absolute scalar error 29; at size 256 it was 906/1,024 and
error 88. This is descriptive across only four source clusters, not a clean size effect.

For clusters 0–2 at both sizes, the predicted and oracle qualifying-user sets matched, but
wrong labels changed per-record contributions and therefore the scalar. Cluster 3 also
changed threshold membership: the size-64 prediction retained one rather than two users,
while size 256 retained three rather than two. Across episodes, 61 record contributions were
nonzero relative to the oracle reducer. A high whole-map label accuracy is therefore not an
adequate proxy for exact aggregation on this task.

| Cluster | Size | Labels correct | Predicted | Gold | Absolute error | User set match |
|---:|---:|---:|---:|---:|---:|---|
| 0 | 64 | 58/64 | 81 | 82 | 1 | yes |
| 0 | 256 | 229/256 | 238 | 254 | 16 | yes |
| 1 | 64 | 55/64 | 47 | 54 | 7 | yes |
| 1 | 256 | 224/256 | 174 | 196 | 22 | yes |
| 2 | 64 | 57/64 | 54 | 48 | 6 | yes |
| 2 | 256 | 227/256 | 156 | 148 | 8 | yes |
| 3 | 64 | 53/64 | 0 | 15 | 15 | no |
| 3 | 256 | 226/256 | 148 | 106 | 42 | no |

# Native and cost audit

The prospective reader reconciled all 40 frozen coordinates with the exact request body and
wire hash, model, native prompt/completion evidence, finish branch, recorded coordinate, and
recorded score. The physical union contains 40 REQUEST, 40 RESPONSE, and 40 RESULT artifacts.
All responses were HTTP 200, choice-bearing, authenticated `stop` completions; there were no
malformed maps, missing batches, or NULLs. Usage was 71,426 input tokens, 24,629 output tokens,
and 37,520 cached input tokens, with no unknown usage fields.

The owner completed and released cleanly. The parent exited 0 without timeout after 124.528
seconds and reported no remaining GPU process.

# Interpretation and next decision

This is a child-label ceiling under an experimenter-authored executable plan, not evidence
that a root learned planning, acquisition, or aggregation. It cleanly rules out “correct plan
alone makes current c32 exact at scale” for this small panel. It does not show that the plan
is optimal or compute-matched to free-root runs: the 40 calls use newly sampled predicted
maps, not identical child outputs.

The next discriminating intervention should target classification uncertainty without using
gold repair—for example, a prospectively fixed selective second pass over low-confidence
records—while retaining all original predictions and charging the extra calls. Repeating the
same supplied reducer without changing child evidence has little information value.

# Evidence

- Native audit: `AUDIT.json`, SHA-256
  `a68c97bf290d4abaa88b668899cecd9e0ad12b8db53d8ccf4389abc8929d360e`.
- Frozen method: `METHOD.md`, SHA-256
  `74a2e0eda71081dfd1e701ec5337835587abec1017719fef606fba1f16ef3462`.
- Producer READY: SHA-256
  `33feec97b7ed3e1238acb7b750441ceac5caceaf67f370222e697bc861d834e7`.
- Owner terminal: SHA-256
  `0b6034ac31854444f1bb2101a13ca88f86ff5ef0faeaa3b342aeb5efbd6bffd7`.
- Parent EXIT: SHA-256
  `9160822abd3bf910025f8debe82b8fa4cb3e5fee470ecfcc7588486cfb34e8d3`.

This reviewer authored the producer and prospective reader. The raw audit was frozen before
outcome inspection but is not author-independent.
