---
id: mnli-visible-reference-wording48
status: completed_exploratory
question: Can explicit same-record instructions remove misleading-identifier interference?
evidence: AUDIT.json
contexts: 8
planned_calls: 48
available_calls: 48
claim_level: replicated_local_effect_not_general_equivalence
---

# Clearer instructions did not remove the identifier penalty

The model classified the displayed text much less accurately when its required
output identifier also named a different visible record. Explicitly explaining
that the identifier was only an output address left this large penalty intact.

| Visible identifier | Earlier wording | Explicit same-record wording |
| --- | ---: | ---: |
| Names another record | 146/384 (38.0%) | 152/384 (39.6%) |
| Unrelated identifier | 308/384 (80.2%) | 313/384 (81.5%) |
| Matches output address | 313/384 (81.5%) | 318/384 (82.8%) |

Every one of the eight contexts showed a misleading-identifier penalty under
both wordings. Relative to the aligned condition, that penalty was43.49
percentage points with earlier wording and43.23 with explicit wording. The
wording intervention therefore reduced the mean penalty by only0.26points;
its context signs were3 positive,3 negative and2 tied. This is not an
equivalence test and does not establish that wording can never help.

Where the displayed and differently named records had different gold labels,
the model favored the named record's label in179/258 cases under earlier
wording and177/258 under explicit wording. The displayed record's label
appeared in43 and46 respectively, with36 and35 third-label responses.
These are conditional diagnostics, not independent examples or causal proof.

## What was held fixed

The full three-reference by two-wording comparison used eight contexts of48
MNLI examples, four genres, and128 distinct premise groups. Texts, record
order, requested output-tag sequence and exact-tag output grammar stayed
fixed within each context. Only visible identifiers and instruction wording
changed. One paired seed per context, released Qwen3-4B Instruct2507 without
an adapter, temperature0.5, no tools or thinking, and no prefix cache were
used. Explicit wording added eight natural tokens; there was no artificial
padding. These contexts were new relative to the named prior inventory at
selection, not guaranteed unseen in pretraining. Multiple hypotheses share
premises. Do not treat384 labels as384 independent contexts.

## Evidence and cost

All48 responses passed independent native-token, actual-request and complete
output-contract checks. No primary NULLs, unexpected physical calls or
producer-score disagreements occurred. The actual base service identity was
verified and every captured service process exited. Known physical usage was
183,324 input and46,167 output tokens, cache0, with no unknown usage fields.
Owner time was311.525seconds; parent time314.088seconds. These are wall times,
not optimizer or precisely measured active GPU seconds; no training occurred.

The original reader was authored by bridge_audit, who had authored predecessor
readers but not this six-arm experiment. MAIN read its full source and tests,
reran seven focused tests (0.04seconds), inspected two raw response branches,
and revalidated all177 frozen output pins without disagreement. The author's
earlier eight-test qualification included the full native48 CPU fixture;
MAIN did not rerun that fixture. All48 native checks in AUDIT.json are actual
experimental-response checks, not the fixture.

## What this changes

This strengthens the local finding that well-formed, exactly addressed JSON
can still carry the wrong record's answer. Our next experiment asks whether
writing the label before the identifier reduces the penalty. It changes the
interface, not model weights. Do not claim that field-order sensitivity or
structured-output errors generally are novel; nearby literature must be
considered alongside our narrower fixed-output identifier manipulation.
