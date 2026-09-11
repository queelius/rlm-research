# Post-hoc: ordinal labels mostly follow source numeric IDs

This diagnostic was specified after seeing poor ordinal displayed-position accuracy
but relatively good label histograms. It is explanatory, not a preregistered endpoint
or replacement score. Original METHOD.md, AUDIT.json and REPORT.md are unchanged.

All 32 original ordinal wire responses were read once. Strict JSON, exact 64 tags,
canonical labels and a bijection of source q0001–q0064 were checked. Comparing each
emitted pNNNN label to source qNNNN, rather than its instructed displayed record,
substantially improves diagnostic agreement in **every call**.

| Task | Original displayed position | Diagnostic numeric source ID | Item gains/losses | Histogram-preserving chance | Context-majority baseline |
| --- | ---: | ---: | ---: | ---: | ---: |
| TREC | 287/1024 (28.0%) | 859/1024 (83.9%) | 662/90 | 220.56/1024 (21.5%) | 296/1024 (28.9%) |
| SST-2 | 505/1024 (49.3%) | 953/1024 (93.1%) | 492/44 | 519.44/1024 (50.7%) | 560/1024 (54.7%) |

The chance reference randomizes correspondence while preserving each actual
predicted-label histogram; it is not an independence-based significance test.
Every context improves (four calls, denominator256 each): TREC contexts0–3
72→206,79→225,54→217,82→211; SST contexts4–7
115→247,126→228,126→236,138→242. Presentation0 improves404→907/1024,
presentation1 improves388→905/1024. Each seed (227909818 and1362606574)
improves396→906/1024. The machine-readable artifact retains every joint
task/context/presentation/seed coordinate, not just marginal summaries.

Confusion becomes strongly diagonal. For SST, displayed gold-negative is
233 negative/271 positive and gold-positive248 negative/272 positive;
numeric-ID alignment gives457/47 and24/496 respectively. For TREC, numeric
diagonal counts (abbreviation,entity,description,human,location,numeric) are
11,200,206,124,135,183; the largest remaining confusion is description→entity46.
Both complete confusion matrices, all coordinate counts and hashes of all32 raw
files are preserved in POSTHOC_NUMERIC_ID_AUDIT.json.

This supports interference from the shared numeric ID suffix: the model often
uses a source identity even when the output prefix differs and the instructions
assign tags to displayed positions. Classification may remain substantially right
while its assignment violates the requested task. It does not rescue ordinal
accuracy, establish counter success, demonstrate hidden attention, or turn these
exposed contexts into confirmation. Meaningful and constant primary arms were not
rescored. A prefix swap alone retains the shared-suffix conflict; a future neutral
counter control should also prospectively remove numeric-ID overlap.

Verification: an adversarial 64-record reversed-ID fixture gives0/64 displayed
versus64/64 numeric agreement, demonstrating that the implementation distinguishes
the two alignments. Actual original displayed totals exactly reproduce the frozen
audit. No new inference, model calls or receipt outcomes were used.
