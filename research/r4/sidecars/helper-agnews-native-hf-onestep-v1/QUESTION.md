# AG News B4 native/HF one-step pilot

Can a qualified one-step helper update on128 new AG News records, using B4 maps
and correct-count RLOO, improve the fixed AG heldout256 readout relative to c32?

The exact approved protocol and source pins are in
`ideas/2026-09-12-agnews-native-hf-one-update.md` (SHA
`0ea086c77c74be35ce59a889324d07016e91bc296ef7911998e2c44c5c7f021d`).
QUESTION.yaml and READY record the executable dose, seeds, caps and gates.

Native128 calls are32 label-blind B4 groups x4 completions at temperature0.5.
Each of the128 training records is presented four times; the reward is fraction
correct times4, so the RLOO advantage is a correct-count difference. Equal-reward
groups remain zero contributors to the fixed128 denominator. Fresh c32 and fresh
AdamW are used; no four-step checkpoint, historical native actions, or heldout
record is a training input. BF16 base/FP32 LoRA, SDPA, dropout off, exact ordered
grammar and completion-only loss remain fixed.

One V4 batch-invariant native service collects actions and releases completely.
Native Python with CUDA hidden builds the exact XGrammar masks; the training
environment does not import XGrammar. One HF model load performs both scoring
and gradient replay. Every importance and replay gate must pass before the
optimizer is created. Error, incomplete collection, no signal or gate failure
stops without an update; all artifacts remain. A post-step save failure is not
an eligible checkpoint and records completed/uncertain step evidence explicitly.

Maximum prompt1133 + completion1024 =2157, below the unchanged service cap8192.
The native owner confirms the actual runtime configuration and final kernel
marker. Training owner/external caps are1100/1200 seconds; phase caps650/60/350
plus40 reserve. The parent supplies shared-lock scheduling. This sidecar does
not reserve or acquire GPU ownership itself.

The updated evaluator uses the existing exact AG256 V2 native schema,64 B4 calls,
temperature0 and fixed seeds. The original c32 READY_C32_V2 is preserved; reuse
its results only after matching actual runtime and complete raw qualification.
Otherwise obtain a fresh baseline. Eval caps600/700 per arm. Always report
correct/256, missingness, paired wins/losses and per-class confusion; raw training
reward and step completion are not heldout improvement.

This bundles new domain/data, request granularity, reward and dose. Positive net
paired wins motivate only a fresh-seed replication, not a confirmed improvement.
No heldout outcome chooses records, checkpoint or a continuation. The existing
AG true-HF four-step source remains separate and conditional.

The frozen AG train/heldout manifests exclude verified c32 SFT5065, current32,
old256, fresh-adaptive128 and known root IDs/normalized texts, with zero train/
heldout normalized overlap. This is not a base-pretraining exclusion claim.
The pinned dataset card's license was unspecified; local research only, no
redistribution right inferred. Once current readouts are inspected the panel is
research-exposed, despite remaining outside helper optimization.

Tests use real four-key native token decoding, host reward, exact grammar/EOS
masks and actual runtime context shape; and tiny real HF/PEFT scoring/backward/
AdamW, including importance and replay failures leaving the weights unchanged.
