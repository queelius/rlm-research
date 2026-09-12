---
kind: research_operations_observation
created_utc: "2026-09-12T11:34:00Z"
status: source_inspected_observed_timings_not_matched_speed_benchmark
---

# Why a short optimizer update can sit inside a long experiment

The original true-HF helper trainer samples autoregressively and replays each
sampled token with another full-prefix forward pass, without a key/value cache.
When the reward advantage is nonzero it also backpropagates at each token step.
This was a useful exact-policy qualification route, but it repeats substantial
work. Source: `../sidecars/helper-hf-onpolicy-v1/train.py::replay_group`, especially
the loop over `record["steps"]`, `prefix_logits`, and `loss.backward()`.

The completed fast48 route instead collected with native serving, measured HF
trajectory probabilities, and used detached importance weights. It checked the
differentiable full teacher-forced sequence path against its pre-step HF scores,
then made one optimizer update. All48 replay checks passed. Its actual trainer
time was36.309s; the source collection owner took166.766s and likelihood recovery
16.827s. Evaluation and prior failed setup/qualification efforts are additional
costs. See `../analyses/fresh48-fast-one-update-2026-09-12/REPORT.md`.

These are different workloads and estimators, not a matched speed experiment.
The 48 actions are whole16-record maps over two familiar contexts, whereas the
true-HF reference uses128 singleton actions per update. Do not quote a raw
training-time ratio as an end-to-end speedup or claim a new accuracy benefit:
the fast update's256 evaluation labels matched the four-step reference exactly.

Decision: finish the already accepted paired reward-baseline control unchanged.
For new exploratory training, prefer investigating the already qualified native
collection/full-sequence HF path instead of extending the expensive tokenwise
replay implementation. Preserve support, importance, gradient-path, data-split,
and checkpoint evidence. The broader AG128 batch-four one-update package is
being prepared on CPU; it is not yet a completed or admitted GPU experiment.

This note records an observed computational cause, not a reason to relax a
failed probability gate or discard failed attempts from experiment accounting.
