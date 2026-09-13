---
schema: b05-state-representation-mechanism-note-v1
source_report: REPORT_V2.json
source_report_sha256: 43402261d570a265484a1c4f2484ba48075feba9897d2fd2000964029a0594e8
context_units: 12
paired_seed_units: 24
physical_calls: 72
---

# Candidate grouping helps before resolution; resolution mainly restores recall

All 72 planned calls returned valid native responses under the authenticated runtime: 24 per view,
with no unknowns. The twelve roots and their candidate IDs regenerate exactly and are disjoint from
the prior normalization panels and the sealed decision-vector panel. Every grouped unresolved record
contains the unchanged base candidate plus every applicable public update and check row; it performs
no delta arithmetic, latest-check choice, eligibility computation, or filtering.

| view | exact / 24 | mean BA | TP | FP | FN | TN | prompt tokens |
|---|---:|---:|---:|---:|---:|---:|---:|
| raw tables | 1 | 0.59289 | 158 | 59 | 26 | 17 | 102,048 |
| grouped unresolved | 4 | 0.75632 | 153 | 28 | 31 | 48 | 108,788 |
| resolved records | 8 | 0.84039 | 174 | 29 | 10 | 47 | 48,856 |

All three views were semantically valid on all 24 matched seed units. Grouping versus raw produced
3 exact wins and no losses (1 both exact, 20 both wrong); BA rose 0.16343. Its aggregate mechanism
was conservative selection: 31 fewer false positives and 31 more true negatives, at the cost of 5
true positives. This gain cannot be attributed to shorter input—the grouped prompts used 6,740 more
prompt tokens than raw.

Resolution versus grouping produced 4 further exact wins and no losses (4 both exact, 16 both wrong);
BA rose another 0.08407. Here the mechanism was primarily recall: 21 more true positives and 21 fewer
false negatives, with only one extra false positive. Raw to resolved therefore yielded 7 exact wins,
no losses, and a 0.24750 BA increase.

Concrete cases show the distinction:

- On `root_741ed08a71b3d5`, raw selected every true item but also 3/1 extras across the two repeats;
  grouping alone removed the extras and was exact both times. Resolution made no further difference.
- On `root_0fd3618d3b24bb`, raw missed one true item and grouping missed two; only resolved records
  recovered all four true items, exactly in both repeats.
- On `root_d832f6a8404885`, raw and grouped views retained one false positive in both repeats; resolution
  removed it and became exact.
- The effect is not uniform in BA: on a width-20 case (`root_29eed70...`), grouping chose 10 true and
  zero false items (BA 0.857), whereas resolution chose all 14 true plus 6 false (BA 0.5). Aggregate
  and exact improvements do not imply every resolved instance was better.

This is evidence that candidate-local public organization helps the fixed model even without host
resolution, and that mechanical resolution adds a distinct recall benefit. It is not a token-matched
causal isolation: representation wording and length both change, the tasks come from the same
generator family, and no learned decomposition or routing is tested.

The initial `REPORT.json` is preserved. It reported three false audit issues because it compared the
independent additive `invalid_known` field against source summaries that do not define that field.
`REPORT_V2.json` removes only those three optional-field mismatches; all wire, runtime, transform,
grade, cost, and outcome data are unchanged, and its issue list is empty.
