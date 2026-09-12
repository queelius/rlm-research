---
question: Did the fixed final-only RLOO step change behavior on its original fresh8 training batch?
scope: in-sample paired behavioral diagnostic, not held-out transfer or a new optimizer run
model: original cp32 plus fixed qualified fresh8 RLOO checkpoint-0001
planned_episodes: 32
independent_contexts: 8
seeds: 202609250000..202609250031
science_seconds: 900
owner_seconds: 1100
external_seconds: 1200
---

The existing transfer readout is flat on short held32 and long16; the one exposed four-needle exact win is two restored spaces. This missing training readout distinguishes in-sample rollout fit from a change visible only in teacher-forced probabilities. No update or new examples are added.

Reuse all eight original fresh8 training contexts, four original seeds each, exact original serialized inputs and initial token prefixes. New root is the already-fixed qualified RLOO checkpoint, not a selected endpoint. Reuse the completed cp32 control (7 exact/32 available), with its full raw/native provenance. Baseline and new weights differ; matching seeds does not imply identical generated tokens. These contexts and outcomes were used by the update, so this is not generalization, independent replication, or model selection.

Same temperature .5, 2048 tokens per action, six total root actions, zero children, four workers, native parser/template, terminal-strip-disabled hooks and original official scorer. Preserve every scheduled episode, raw request/response checkpoint and missing/error branch. The inherited science result includes a legacy `manipulation_gate` field from the original procedural screen; it is explicitly inapplicable and never gates this readout or a subsequent job. Owner completion uses runtime/schema/cap integrity only, never accuracy.

Primary comparison: exact C/W/U and paired wins/losses over all32 planned, with eight context-level G4 vectors. Secondary: correct program/clean stdout vs final copying, unchanged official score, every changed action path, missingness and total native costs. Inspect boundary errors (two spaces, extra newline, EOS) separately from literal-selector/tool serialization changes. All32 retained, including20 zero-advantage source trajectories; no filtering to12 trained finals.

If in-sample exact improves but transfer remains flat, report local copying fit rather than new retrieval/delegation ability. If flat, do not infer unchanged probabilities or automatically escalate dose; review train-path/boundary changes before another optimizer decision. Regression also does not trigger an automatic retry. No predeclared accuracy threshold authorizes training here.

Source seams: `study.py` redirects only the schedule/environment to the immutable original fresh8 screen; `checkpoint.py` calls the existing complete tensor/Adam/RNG/source/replay qualifier in its original module scope; `collect.py` and `owner.py` load the existing accepted collectors/owners under scoped aliases. No frozen originals modified. Focused CPU fixture checks real environment setup, all32 old coordinates, sampling, inner collector aliases and actual checkpoint qualification.

MAIN only, after review and shared exclusive GPU lock, runs under an external1200-second timeout:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py run --phase train
```

Output is `outputs/train-001`. Source verification, CPU only: same Python `owner.py verify --phase train`. Existing finite owner authenticates service/model binding, checkpoints each call/episode and releases its owned service. No model weights are changed; no sampling occurs in preparation.
