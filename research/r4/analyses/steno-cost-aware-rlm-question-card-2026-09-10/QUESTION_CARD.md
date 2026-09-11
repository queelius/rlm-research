---
date: 2026-09-10
status: primary_source_review_complete
question: Does a lower RL learning rate stabilize our very-small composed-task RLVR dose?
---

# Cost-aware RLM RLVR: what it changes for our next test

Steno's 61-page University of Twente thesis is unusually close in model family and training stack,
but far from a matched replication. It trains Qwen3-4B-Instruct-2507 with Prime-RL and LoRA on a
35% aggregation / 40% deep-research / 25% long-code mixture. The rank/LR sweep covers ranks
4/16/64, learning rates 5e-7/1e-5/1e-4, and as many as 150 optimization steps. Each step consumes
64 rollouts arranged as 16 prompt groups of four; the run uses eight A100-80GB GPUs, four for
rollout and four for training. These are thesis-reported conditions, not results reproduced here.
See the [thesis PDF](https://essay.utwente.nl/fileshare/file/110199/master-thesis.pdf) and the pinned
[official code/config repository](https://github.com/lsteno/prime_run).

The closest useful contrast is objective scale and credit assignment. The thesis uses four attempts
per prompt and mean-centered group-relative advantages without standard-deviation normalization.
Its root/recursive policy tokens are trainable, while external subcall and observation tokens are
masked. Failed traces mask all completion actions. Correctness is binary, but an adaptive within-group
token-cost term turns on only above a 0.25 solve rate: beta is 0/0.05/0.10/0.15 for at most 1, 2,
3, or 4 correct attempts; forced finalization can subtract 0.25. All-zero groups are withheld for a
five-step cooldown rather than treated as useful updates. The released rank-64 configuration pins
AdamW, LR 1e-5, zero weight decay, norm clip 1, KL 1e-3, rank64/alpha128 across all attention and
MLP projections, IPO masks 0.2/0.2, maximum off-policy age four, and a 400-second rollout timeout.
These details are directly checkable in the [official rank-64 config](https://github.com/lsteno/prime_run/blob/2d57d15916f5fa0deed64c21d2e83f02a394afda/configs/rlm_rlvr/ablation_rank_lr/qwen3_4b_instruct_sanjaya_depth1_llmonly_r064_a128_lr1e-5_s150_8xa10080_bal35f40v1.toml).

The reported aggregate 270-example long-context score rises from 27.0 to 37.6 for selected rank64,
LR1e-5, while depth2 is slightly worse than depth1 and invokes recursive sub-RLM calls in only 0.1%
of rollouts. The thesis explicitly limits this to its Qwen3-4B harness, selected checkpoints, task
mixture, and single training seeds; its lower-cost finding is for the whole shaped setup, not an
isolated cost-penalty causal effect. The public [artifact collection](https://huggingface.co/collections/lsteno/qwen-3-4b-rlm-rlvr)
is the appropriate source for released model/data/evaluation receipts.

The learning-rate table makes optimizer scale decision-relevant but does not determine our answer:
all three rank settings underfit at 5e-7, whereas rank64 at 1e-4 became unstable and stopped after
72 steps; rank64 at 1e-5 was the strongest completed LoRA validation-p@1 point. The thesis never
tests our 5e-5 rate, rank8 adapter, specialized start, or tiny update count, so 1e-5 is a bounded
stability probe rather than a claimed optimum transfer.

Our current counterevidence is therefore not evidence that root RLVR generally fails. The
checkpoint-2 readout released at 2026-09-10 21:44 UTC; the separate high-LR sparse continuation
launched at 21:47, committed step 3 at 21:53 and step 4 later, and was around window 7 at 22:09.
These are interim operational milestones, not its terminal result. Our run starts
from a task-specialized QS6 adapter, uses rank8, LR5e-5, at most eight small windows of six groups x
four samples, population-standardized advantages, terminal correctness only, TIS cap2, and a fixed
c32 child. Even the planned eight-update dose is orders of magnitude smaller than 150 x 64 rollouts; many
homogeneous reward groups also yield exactly zero centered advantage. Model size and group size
match, but optimizer scale, rank, task distribution, reward, filtering, asynchronous staleness, KL,
and compute do not. The thesis supports continued bounded testing, not importing its headline.

## Smallest informative GPU follow-up

Run one exact lower-LR continuation from the same QS6 root and c32 child: preserve the current
composed48 tasks, eight fixed windows, four samples per group, seeds/order, binary verifier,
population-standardized group advantages, PPO/TIS/masks, no refill, fixed-last policy, and protected
72-task panel. Change only AdamW LR from 5e-5 to 1e-5. Keep rank8 because changing rank would require
a new start adapter and confound the comparison. Cap at eight actual updates and 192 planned training
attempts. Reuse the already authenticated 72 QS6-start endpoints and make only 72 new fixed-last
calls. Allow up to 12,000 seconds for training, including an unchanged 1,800-second cap for each
optimizer subprocess, plus a separately reserved 2,700-second readout and cleanup/parent margin.

Falsifiable readout: lower LR is useful if it preserves at least as many actual admitted updates,
reduces optimizer/mask/pathology evidence, and improves the fixed protected paired endpoint without
increasing availability failures. If it again produces few actual updates because reward groups are
homogeneous, retire LR as the immediate bottleneck and next test the thesis-inspired adaptive-cost
credit on retained traces before any GPU launch. That second step must first show offline that
within-group observed token costs create nonzero mean-centered advantages; it should not be bundled
into the LR ablation.

Acquisition receipt: PDF SHA-256 `9b399883fe3bd7561a619d9fc55f649f5b212ff8b59dd989e672a860de6de44c`;
official code commit `2d57d15916f5fa0deed64c21d2e83f02a394afda`; retrieved 2026-09-10.
No thesis or repository-root license was identified, so no redistribution permission is inferred.
