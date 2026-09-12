---
schema: openai-mrcr-cp32-fixed-baseline-rl-update-report-v1
status: complete_read_only
optimizer_steps: 1
new_model_queries: 0
---

# What the fixed-baseline update changed

The checkpoint is internally consistent: every file in `STEP_COMMIT.json` matches, all 504 parent
and updated adapter tensors load, the recomputed adapter displacement is 0.0342144794, and the
recomputed pre-clip gradient norm is 0.0044359505. The saved optimizer is a fresh AdamW state after
one step. Training took 43.74 seconds.

This was not a general root-policy update. Only the 10,420 tokens in the 32 saved terminal actions
received loss; 6,716 earlier root-action tokens and every child token received zero loss. The fixed
0.5 baseline supplied positive advantage to 28 identical-success-status samples and negative
advantage to four repetitions of one failed group. The eight reward vectors were seven
`[1,1,1,1]` groups and one `[0,0,0,0]` group.

The negative signal was highly specific to output delivery. Across the four identical negative
sequences, the isolated negative-gradient norms were:

- body: 4.33e-9
- whitespace: 0.00358407
- EOS: 0.000125416

On the same saved actions after the update, each negative sequence's conditional log probability
fell by 0.07091178. Of that, -0.07091428 came from whitespace, +0.00000250 from EOS, and exactly zero
at saved precision from the 98 body tokens. The 28 positive sequences rose by only 0.00037431 in
aggregate (+0.00001337 mean). Thus the observed update mostly teaches the existing policy to avoid
the failed sequence's extra-whitespace ending; it provides essentially no direct negative semantic
body gradient for that group.

The native/HF correction is not the explanation for this localization: no token weight was capped,
and recorded weights range only 0.99996865–1.00404113 (mean 1.00000093). Replay passed.

## Boundary

This is a useful, real update, but it is not evidence of improved answer selection or accuracy. The
post-step values rescore the same frozen actions; no new completion was sampled. The four negative
examples are copies of one question/one final sequence, and the component norms cover only the
negative gradient, not the combined positive-plus-negative direction. Shared parameters can still
move other behavior indirectly. A new native rollout is required to learn whether the whitespace
change improves exact delivery without harming retrieval.

Machine-readable episode movements and authenticated source hashes are in `RESULTS.json`; the
reproduction script executes no model or generated code and keeps CUDA hidden.
