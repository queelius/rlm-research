---
schema: research-idea-v1
id: dense-feedback-from-rl-direction
created_utc: 2026-09-12T16:11:00Z
status: conditional_literature_lead_not_gpu_ready
priority: medium_after_transfer_and_base_controls
source: https://arxiv.org/html/2609.05295v1
source_date: 2026-09-04
gpu_admitted: false
---

# Can an improving RL direction supply denser teaching signals?

## Primary method, not a local result

RISE forms a teacher by extrapolating between an anchor and a newer RL policy,
then distills the teacher while continuing RL. It supports weight-space and
logit-space versions. The paper explicitly distinguishes distillation from
directly adopting the extrapolated weights; the latter can overshoot. Its
default extrapolation begins at1.2 and decays, with an EMA anchor for its Qwen
experiments. See [Li, Yavuz and Joty, v1](https://arxiv.org/html/2609.05295v1),
method3.1–3.3 and setup4.1. Full appendix reproduction has not been reviewed.

## Why this may matter here

Our two broader RL runs produce nearly identical gains, but only a minority of
sample groups supply reward differences. This creates a plausible opportunity
for an auxiliary distributional signal. It does not show that such a signal
would help; the immediate priority remains the queued independent-data test,
repeated-data mechanism test and raw-base control.

The smallest later training comparison would freeze the same starting checkpoint,
training prompts and initial sampled trajectories, then compare one extra RL-only
cycle with RL plus a fixed auxiliary distillation cycle. Record both owned wall
time and all forward/backward/sample costs; a positive gain with extra computation
is not a matched-compute improvement. Use only training data to settle the recipe
and a newly frozen evaluation panel for a later confirmation.

## Pitfalls before implementation

Our trainable parameters are LoRA factors. Linear extrapolation of A and B is
not generally equal to extrapolation of their product, so it must not be called
the paper's full-weight arithmetic without an explicit construction. A logit
version avoids that ambiguity but adds forward passes and token-distribution
storage. Our grammar-controlled JSON output also contains many forced structural
tokens: determine what distribution is actually trained before claiming denser
semantic credit. Do not build a new distillation stack before current results
show that further helper optimization is useful to the whole RLM.

Prospective resource shape: one4B model sequentially loaded on the existing
A100, at most a30-minute exploratory owner, each update checkpointed. Promote
only if source/raw objective evidence is sound and gains survive a fresh panel;
retire if only training likelihood or already-correct confidence changes.
