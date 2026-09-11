# Additive post-hoc numeric source-ID alignment diagnostic

Declared September9,2026 AFTER exposure to the identity96 result: ordinal tags
had poor displayed-record accuracy but relatively good class-count distributions.
This explanatory hypothesis is outcome-informed, not preregistered. The frozen
METHOD.md, AUDIT.json and REPORT.md remain unchanged. No receipt outcomes are read.

Hypothesis: an ordinal output object tagged p0001 may contain the label for source
record q0001, despite the different prefix and explicit displayed-position
instructions. Randomized source IDs retain matching numeric suffixes. This could
preserve the output label histogram while assigning labels to the wrong displayed
records. It is not successful compliance with the ordinal task.

For all32 ordinal calls only, independently read the exact existing raw response
text and frozen source/design. Retain strict JSON,64-object/tag/canonical-label
checks. Compute (a) original accuracy against the gold at each displayed position,
and (b) diagnostic accuracy against gold of source qNNNN whose numeric suffix
equals emitted pNNNN. Every source q ID must resolve uniquely. No sorting labels,
best-permutation search, label repair, new model call or alternative selection.

Report both counts by task, source context, presentation and sampled seed, all-group
consistency, and paired item gains/losses under the two alignments. Also report
label-confusion matrices for each alignment, per-context majority-label baseline,
and chance accuracy under random correspondence preserving the observed prediction
histogram (dot product of gold and predicted class frequencies). These are
descriptive baselines, not independence-based statistical tests.

Do not rescore meaningful/constant arms as new primary conditions. Do not replace
ordinal's original displayed-position score with the diagnostic score. A large
numeric-ID alignment improvement would suggest that numeric identity competes
with displayed position; it does not prove hidden attention or rescue the neutral
counter claim. A weak/inconsistent improvement fails this specific explanation.
Use one raw-output pass and write separate POSTHOC_NUMERIC_ID artifacts only.
