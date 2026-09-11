# Validation-six milestone — 2026-09-09 02:14:34 UTC

The fixed validation curve is 2/8 → 3/8 → 3/8 → 2/8 at checkpoints0/2/4/6. Val4→6 has one newly wrong and seven unchanged episodes; initial→6 has one gain and one loss. All eight val6 endpoints are observable/admitted; no censoring or integrity failure. Seven terminals are schema-valid. Validation uses two reused contexts/four tasks/two seeds, not eight independent contexts or untouched transfer data.

Actual first-root physical prompt IDs and native sampling match all eight coordinates versus0/2/4. First-root actions differ8/8 versus initial and7/8 versus4. This supports the integrity of the intended root-weight comparison, but the separate unchanged-policy pilot remains only a warning about variability, not this campaign's missing replay control.

Val6 costs 109,564 logical input and 10,444 completion tokens, 103 model calls, 80 recursive subcalls and 15 executed Python calls; one length stop. Rollout elapsed112.904s versus val4's93.332s, with completion cost over twice val4's4,705 tokens. These are descriptive cost changes, not a reliable causal worsening claim.

Step6 is a genuine Adam5→6 update across504 states:15 mixed episodes/39 root turns/11,660 root tokens, no child/observation credit, gradient0.14403975, delta L2 0.09381248, optimization36.796s, all guards pass. Total actual updates6/root tokens85,791. Fresh-seed collection6's16/32 correct endpoints are not a learning curve. Its one excluded wrong episode has two raw authenticated unsampled child context-overflow errors; admitting its1,695 recovered root tokens remains explicitly outside this amendment.

Decision: no learning improvement established, no early selection or recipe change. Continue the remaining original stages to distinguish the fixed validation-selected checkpoint from the last step8 checkpoint and report fresh transfer separately. This is still a small exploratory RLVR run, not a basis for retiring the general learning hypothesis.

Snapshot SHA256 `d4b9bac00259a1b5329b9508173fd64a45c5d40fac00aaea2349bc842ffddd94`; first-action audit SHA256 `774803792cb8077998611775f1718c0bcac944d7b9ab70459cef2ffa62516d2f`; raw exclusion audit SHA256 `e220daaed3ff4fefe5a04198b8bf09055f86cacc418a1f7715e09d8896c5b9a7`. No GPU calls or runtime/source changes.
