---
schema: research-idea-v1
created_utc: 2026-09-12T20:21:00Z
status: exploratory_comparisons_in_cpu_preparation
priority: high
question: Is the trained controller too repetitive to supply useful group-relative rewards?
trigger: openai-mrcr-sft32-g4-mechanism-2026-09-12/MAIN_REPORT_001.json
model: Qwen3-4B-Instruct-2507
training_split: first_8_original_MRCR_train_contexts
heldout_training_prohibited: true
---

# A competent controller can still give RL no learning signal

The fixed checkpoint32 produced28 exact answers in32 attempts. Every one of
eight questions had four identical returned answers. Seven groups were all
correct; one repeated the same copying error four times. All32 programs
matched their teacher program and printed the correct target text. All eight
groups therefore have zero reward variance and all RLOO advantages are zero.

This is not evidence that a learning rate is too small or that credit went to
the wrong turn: there is no reward contrast to assign in the first place.
We will not take a zero-gradient optimizer step simply to label it RL.

## Two small comparisons

The completed condition is checkpoint32 at temperature0.5. Prepare two new
conditions, keeping all eight contexts, four attempts, requested seeds,
limits, exact grader and output-preservation hooks fixed:

- Checkpoint32 at temperature1.0 asks whether more varied sampling produces
  useful successes and failures while retaining the retrieval procedure.
- The predetermined intermediate checkpoint16 at temperature0.5 asks whether
  less supervised training retains enough competence with more variation.

These are separate one-factor contrasts with the completed condition, not a
full dose-by-temperature factorial. Neither checkpoint nor question subset is
chosen from its new outcome. Each condition has a900-second science cap,
1100-second owner cap and1200-second external cap on one A100. Save every
native token path, selected-token log probability, answer and checkpoint hash.

Promote a condition to an RL candidate only if complete groups supply genuine
reward contrast. Compare correct-target tool observations and actual final
answers before choosing a loss mask. If at least two groups offer useful
contrast, a paired all-root versus final-text-only update can distinguish
credit assignment while keeping the starting policy and episodes fixed.
Retain zero-advantage groups in the normalization. Do not mistake the last
tool action for a completed final answer. If higher temperature only destroys
program competence, favor new training examples or an earlier competent dose.

## Related primary research and what it changes

[ClawGym II, arXiv2608.16798v1](https://arxiv.org/html/2608.16798v1),
dated August17, describes training through model-call capture, preserving the
original generated tokens, counting shared actions once, and correcting
training-versus-serving probabilities with capped token importance weights.
It excludes auxiliary agent trajectories from its main-agent optimization.
These methods are prior art, not our invention. Its approach supports keeping
our actual sampled tokens and separating numerical policy mismatch from the
newly observed absence of reward contrast. Main read methods3.2 and the
experimental setup on September12; no third-party code was acquired here.

[ECHO, arXiv2605.24517v1](https://arxiv.org/html/2605.24517v1), dated May23,
adds an observation-prediction loss to action-token policy learning. It uses
existing environment responses as additional targets and reports degradation
when that auxiliary objective is too strong. Main read methods3.1–3.3 on
September12; no code or weights were acquired. This suggests a later bounded
comparison if useful group-relative contrast remains scarce. It does not
justify calling ordinary observation prediction RL or assuming that learning
to predict retrieved prose will improve which evidence the model selects.

For us, copying the environment's large arbitrary text could dominate such
an auxiliary objective. Any experiment would separately measure new-context
retrieval, exact final delivery, and short environment-structure prediction.
Queue it below the two direct contrast tests, not ahead of ready GPU work.

Sources are versioned web readings, not pinned executable dependencies.
Source method claims above are distinct from our proposed experiments and
from our local measured28/32 result. Full-distribution entropy was not measured;
four sampled answers and chosen-token surprisal are only limited diagnostics.
