---
status: complete_manual_semantic_segment
date: 2026-09-10
study: root-question-sensitive-seed-replication-v1
policy: unchanged
segment: [72, 143]
planned: 72
observed: 62
null: 10
authenticated_empty_observed_zero: 8
strict: 25
faithful: 22
faithful_and_strict: 16
grounded_faithful_and_strict: 15
reviewer: independent_subagent
---

# Fresh-seed unchanged-policy semantic review, indices 72–143

## Result

All 72 planned unchanged-policy rows were reviewed. Sixty-two are available
observations and ten remain NULL under the qualified audit availability rule.
The eight authenticated empty finals are observations with strict score zero,
not NULL.

Among the 62 observed rows, 25 are strict, 22 implement the requested operator,
scope, targets, and threshold, and 16 are both faithful and strict. Index 92 is
the important boundary case: its reduction expression is faithful and its final
is strictly correct, but the model overwrote the complete map and every reduction
attempt failed. Its final therefore does not use an observed scalar. Requiring
faithfulness, strictness, and an observed-state-supported final leaves 15/62.

Faithfulness is concentrated in primitives: count 6, distinct-users 7, and
weight-sum 6. Only three composed cases are faithful (two conditional-weight and
one maximum-weight), and no threshold-users case is faithful. Many exact answers
are therefore coincidences: 9/25 strict rows use an unfaithful reduction.

## Wrong answers with faithful reductions

Four grounded faithful reductions are wrong strictly because the actual child
labels differ from the protected labels. Applying only the trusted
`qs_problem.answer` oracle to each actual complete child map reproduces its final:

| Index | Task | Actual-map oracle | Final | Host gold |
| ---: | --- | ---: | ---: | ---: |
| 83 | P1 count, ADJ, numeric value | 0 | 0 | 1 |
| 91 | P2 distinct users, ODD, numeric value | 2 | 2 | 1 |
| 113 | P3 weight sum, ALL, description/abstract | 19 | 19 | 15 |
| 118 | P3 weight sum, ALL, description/abstract | 17 | 17 | 15 |

This diagnosis uses the actual returned child maps. It does not replace the
strict protected score or infer labels from record text.

## Availability and failure accounting

- Authenticated empty observed-zero indices: 75, 87, 90, 107, 110, 124, 138,
  141.
- NULL indices: 74, 77, 80, 86, 97, 102, 119, 123, 131, 134. Index 119 is
  `native_unverified_or_unresolved`; the other nine are
  `attempted_missing_result`.
- Acquisition across all planned rows: 59 complete, 2 partial, 1
  attempted-but-failed, and 10 NULL. “Complete” records that labels were observed
  for all 16 records; it does not imply that the program retained a merged map.
- Classification counts: 15 grounded faithful-strict, 1 faithful-strict but
  unsupported final, 4 faithful wrong due to actual child labels, 9 unfaithful
  strict coincidences, 25 unfaithful wrong, 8 observed format failures, and 10
  NULL.

The per-row JSON keeps acquisition, complete-map retention, semantic
faithfulness, observed-state final support, strictness, their conjunction, oracle
diagnosis, classification, and a concrete note separate. This matters for cases
such as indices 90 and 124, where a correct reduction was written but map handling
prevented execution, and index 92, where the unsupported final happened to equal
gold.

## Review method and limitations

The review read every available row's sampled programs and parent-linked tool
observations in the qualified audit JSON. Sampled programs were not re-executed,
and no keyword classifier or host-side semantic substitute was used. The trusted
`qs_problem.answer` oracle was invoked only on actual observed child-label maps to
diagnose the faithful cases listed above and the explicitly noted failed-map
boundary cases.

“Retained complete map” means a complete decoded ID-to-label map survived in the
actual program state for the attempted reduction. It is stricter than acquisition:
several rows observed all labels across calls but overwrote or failed to merge
them. “Final uses observed state” requires an observed integer scalar supporting
the returned final; equality to gold alone is not evidence. The semantic judgments
are manual and necessarily encode interpretation at malformed-program boundaries;
the JSON notes expose those decisions row by row.

## Exact sources

- `METHOD.md`: `208ed6a52606bdad8fd55f2c43b776d944eef0ea80d7b06aed8c7c67070926b7`
- `readout_audit.py`: `812f2b468d5bdbfccb55cd0ffb40e53314cba2711aaa2443be09036676a8de1e`
- `root-question-sensitive-seed-replication-v1-AUDIT.json`:
  `c680125c138079d485eb16a063b86757398c3a5ecf553821c9064e0e6d839374`
- `sidecars/root-question-sensitive-sft-v1/qs_problem.py`:
  `054029d750c464a0ae8a928ca08d5906a39f4f9334a04d105f65d5bb05a11a4c`

No producer, sidecar, GPU, service, checkpoint, or source repository file was
modified.
