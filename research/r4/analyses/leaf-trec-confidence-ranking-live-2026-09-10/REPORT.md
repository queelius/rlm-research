---
title: Native TREC chosen-token confidence diagnostic
date: 2026-09-10
status: signal_passed_frozen_gate
study: leaf-trec-test-adapter-granularity-v1
---

# Result

The frozen screening gate passes: low mean label-token confidence enriches actual errors in every c32 width/seed cell and after class- and position-stratified sensitivity checks. This motivates, but does not validate, selective rechecking.

The primary score is the mean chosen-token log probability over only the emitted label span. A random 25% review budget covers 25% of errors in expectation.

| Cell | Errors | Mean-score error recall | Class-stratified | Position-stratified | Sum-score recall |
|---|---:|---:|---:|---:|---:|
| base:W:repeat0 | 180 | 37.8% [37.8, 37.8] | 38.2% | 37.8% | 36.7% |
| base:W:repeat1 | 180 | 35.8% [35.6, 36.1] | 36.2% | 35.3% | 35.8% |
| base:S:repeat0 | 141 | 41.8% [41.8, 41.8] | 41.2% | 44.3% | 43.4% |
| base:S:repeat1 | 142 | 43.7% [43.7, 43.7] | 42.2% | 43.8% | 43.7% |
| c32:W:repeat0 | 80 | 67.5% [67.5, 67.5] | 65.3% | 64.4% | 60.0% |
| c32:W:repeat1 | 75 | 64.0% [64.0, 64.0] | 62.0% | 61.7% | 60.7% |
| c32:S:repeat0 | 57 | 66.7% [66.7, 66.7] | 68.4% | 67.1% | 64.9% |
| c32:S:repeat1 | 58 | 69.0% [69.0, 69.0] | 70.3% | 67.7% | 67.2% |

Combined descriptively across the two seeds (without reranking across seeds):

| Model/width | Errors | Mean-score recall | Class-stratified | Position-stratified |
|---|---:|---:|---:|---:|
| base:W | 360 | 36.8% | 37.2% | 36.5% |
| base:S | 283 | 42.8% | 41.7% | 44.1% |
| c32:W | 155 | 65.8% | 63.7% | 63.1% |
| c32:S | 115 | 67.8% | 69.3% | 67.4% |

# Alignment and availability

All 4000 emitted labels across 148 calls were exactly aligned. No label token crossed a JSON boundary, and no record was missing or excluded. Terminal special tokens, IDs, punctuation, quotes, delimiters, and whitespace were excluded.

Both full-sequence decoding and concatenated per-token decoding exactly reproduced every authenticated content string. Native token/log-probability lengths matched and all values were finite. Each captured top-logprob list contains only the chosen token, so alternatives and class margins are unavailable.

# Confounds and limitations

The model-generated JSON order determines prefix position, and every label probability is conditioned on all generated prefix tokens. Label token count is strongly tied to class; sequence sums therefore mix confidence with label length. The mean score reduces but does not eliminate class, lexical, or structured-prefix effects. For c32, gold-class error rates range from 4.9% to 44.4% across cells (the upper extreme is the nine-item abbreviation class), while output-position-quartile error rates range from 8.0% to 21.6%. Yet allocating the review budget within gold class still covers 62.0–70.3% of c32 errors, and allocation within output position covers 61.7–67.7%. Full gold-class, predicted-class, and position tables are in `RESULTS.json`.

Labels within a call are correlated, and the same source records recur across policies, widths, and seeds. The diagnostic is ranking, not calibration, and does not show that requerying changes an answer. Results are reported cell-by-cell with call clustering retained; no record-level significance claim is made. At c32/W the selected records touch all 10 contextual calls; at c32/S they touch 62 of 64 calls, so the ranking is not confined to one call, but this is not an independence argument.

# Prospective follow-up

Conditional on separate supplied-plan evidence showing child-label errors materially limit root correctness, run one paired 25%-budget comparison: recheck the lowest-confidence quarter versus a prespecified hash-uniform quarter, using the same c32 child, source rows, second-pass prompt, and fresh paired seeds. Score corrected child labels and downstream supplied-plan answer separately. Cap at one A100 and 1,800 seconds; freeze all choices and retain failures before launch. This bundle tests selection policy, not confidence calibration.

# Reproduction and pins

CPU-only replay: `/project/alex_phd/envs/prime-rl-5990b1b/bin/python reproduce.py --out /tmp/trec-confidence-replay`. All 148 response/result hashes are in `SOURCE_PINS.json`.

- `adopted_audit`: `1953a24a9e5cd8988b599e8ad5d0d36f4d712f42944853fe604a7e9aee817ebc`
- `adopted_main`: `5adf2e58d49e07c79301e0a9b19242aac99fef029f0cff95fa69c0e006dd1f9a`
- `owner_terminal`: `04c9a038ff97da3404ab392f7f9035a02a7898d24a8e1b301f906f9a69e02bec`
- `parent_exit`: `d1c68b6e3ecabdc367f57cf7e0baeb5f9a8423ba9da4ac5ba998fffcfe9f6a64`
- `rollout_rows`: `0ef34d12cd6d6ff25d377c4048dccc40e929ae248ff92b2ca1490de1142cc331`
- `tokenizer_json`: `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`
- `method`: `3b5a79dc293c5f7fa9b05011c7439a61f922fbb0ac836b5cbc122a6d0cd7e0df`
