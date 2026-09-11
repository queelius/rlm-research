# Does matching-source output survive new sentences and different fixed weights?

Exploratory next-study design, September9,2026 at08:08UTC. Not GPU-ready and not
part of the completed384-call experiment. Main has read its complete independent
report and earlier post-SFT control report. No new outcomes exist for this proposal.

## Why this is the next component check

The completed384-call factorial shows that overlapping numbers worsen position
counters, but removing that overlap leaves a large source-matching advantage.
Every source-context sum supports that difference in both tasks and both prefixes.
The remaining obvious limitation is reuse of eight exposed contexts and one
validation-selected, TREC-trained child checkpoint. Another same-context factorial
is less informative than a small new-source, fixed-weight comparison.

The earlier post-SFT controls already established that original weights have
visible-input/selection failures too. Do not rerun that question. This comparison
asks specifically whether the disjoint matching-ID contrast survives new sentiment
sentences and whether its size depends on the supervised-training checkpoint.
It is not a second model architecture or an independent SFT training seed.

## Smallest informative comparison

Candidate96 native component calls: four new64-sentence SST2 contexts × two fresh
sampling seeds × two source prefixes × two fixed weights × three output rules.
Use disjoint source numerals only, the same exact meaningful/ordinal/constant
schemas and instructions as identity384, and one newly randomized displayed order
per context. Randomized source-ID assignment is independent of sentiment and
displayed position, excludes ordinal numeric/suffix collisions, and remains shared
between weights/arms. Do not cherry-pick IDs for observed model behavior.

Weights are the exact converted original857a7ce6… and historical childc32de129…,
on the same Qwen3-4B-Instruct-2507 revision and renderer. No current RLVR checkpoint
or newly trained adapter may replace either. Compare matched request bodies and
actual physical token prefixes across weights, allowing only the model alias to
change. Reuse a qualified owned native service; do not load Qwen3.5 or install a
new environment solely to broaden this first check.

All labels are scored against the displayed record. Primary is meaningful minus
ordinal in the disjoint namespace, separately for each weight and prefix; report
the weight-by-output-rule interaction rather than only pooled totals. Constant
tags are the retained equal-structure secondary control. Actual token/call costs,
all-array validity, class-count error and complete-array accuracy remain distinct.
Four context clusters, not thousands of independent labels. No overlap-only
numeric-source diagnostic or latent-rank score is available here.

## Source membership and readiness boundary

Use cached SST2 validation revision8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb.
The earlier sentiment study used256 normalized groups, and the later anchor
study used a disjoint256. Preparation must verify their union and every named
SST source catalogue before selecting the first256 remaining normalized-group
hashes. The872-row public split appears to have enough remaining groups; this
is not yet a completed membership check. Do not silently recycle old sentences
if fewer than256 remain. No gold-stratified resampling or balanced label quotas.

Normalization is NFKC, casefold and whitespace collapse, not TREC word grouping.
Check conflicting-label duplicates and report their treatment before freezing.
Preserve dataset source bytes/revision/license uncertainty and source-row indexes.
New to these enumerated studies is not unseen in base pretraining or proof of
whole-history nonexposure. SST2 was not the semantic target of the historical
TREC child SFT, but its prior developmental evaluations remain explicit.

Preparation must freeze exact contexts, seeds/order, weight/renderer/runtime/source
hashes, full typed prompt IDs and launch argv. Use the existing four-worker native
collector with counterbalanced weight/arm order where its proven service path
permits; disclose any phase confounding if a separate service per weight is needed.
No GPU calls during CPU preparation. Bound synthetic parser/group/identity tests
and source verification; do not repeat completed raw audits or broad suites.

Tentative one-A100 shape:96 calls at the prior approximately13s/call with four
workers, plus startup. Expect roughly6–12minutes; proposed1200s inclusive cap,
900s collection,120s owned cleanup. Freeze the exact cap before launch and keep
censored/unrun/provider/model failures separate. No outcome-driven retries.

## What changes after this screen

If both fixed weights retain a large consistent effect on new contexts, prioritize
a different model family or a real RLM consumption test, not more ID-specific SFT.
If only the trained child shows it, investigate how training changes reliance on
output cues. If the new-context effect is weak or inconsistent, narrow the current
claim and inspect source/label/length differences before a larger replication.
The accepted whole-RLM helper-uptake test and preparing child-role pilot retain
higher launch priority. No automatic confirmatory claim follows from this screen.

Sources: completed analyses/identity-factorial-live-2026-09-09/REPORT.md
SHA c70c1743f52ecbcacd263a9903498ee472e0b2971a5e29ee2e94acd642a9078a;
analyses/post-sft-controls-2026-09-09/REPORT.md; pinned source-selection logic in
sidecars/leaf-correspondence-anchor-transfer-v1/study.py and
sidecars/leaf-sentiment-transfer-v1/driver.py. Exact new seed/data identities are
pending preparation, not invented here.
