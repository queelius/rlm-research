# First native-interface 4B RLM policy update

Declared before optimization on 2026-09-08. This is an exploratory one-update
learning test, not a confirmatory comparison or a claim of generalization.

Question: Can a real action-only policy-gradient update be performed on the
model's own correctly captured RLM attempts, and does the frozen evaluation
change afterward?

The input is the complete fresh-training-attempt-001 collection: ten training
questions with four samples each at temperature 0.5. Training questions are
disjoint from interface qualification and source-heldout evaluation. The final
export manifest identifies every raw record and the exact token/logprob data.
Only within-question groups containing both strict rewards 0 and 1 contribute
to the policy gradient. All other collected records remain available for analysis.

The frozen Qwen3-4B-Instruct-2507 base and original rank-8 step-0 adapter are the
starting weights. The single-gpu-rlvr-v2 generic trainer uses seed 950260400,
one AdamW update at learning rate 5e-6, no weight decay, gradient clipping at 1,
and a clipped ratio objective with epsilon 0.2. Advantages are standardized
within question. Weight episodes equally and their model-call turns equally;
only newly sampled action tokens receive loss. Context and observations remain
masked. Captured sampling temperature is used when recomputing policy logprobs.

Use the allocated MIG device only. Stop the owned inference service before
training. Cap the trainer at 30 minutes, with a 90-second shutdown allowance.
Save the adapter, optimizer, RNG, changed-parameter and logprob-drift metrics
immediately after the update. A failed run remains a failed run; do not invent
an update or relax a numerical check without an evidence-based new attempt.

Output: sidecars/single-gpu-rlvr-v2/outputs/4b-native-update-attempt-001.
The shell log is operations/2026-09-08-resume/rlvr4b-attempt001.log.

Replay the same heldout-before task/seed coordinates after training. Report
the predeclared 14-episode primary subset and 16-episode secondary separately.
Neither endpoint chooses training data or hyperparameters. Both use previously
examined context groups and are exploratory. The hint comparison will also be
replayed with unchanged conditions. The independent positive-only self-SFT
control uses the same initial weights and full rollout dataset, but is not
compute-matched to this one-update test.
