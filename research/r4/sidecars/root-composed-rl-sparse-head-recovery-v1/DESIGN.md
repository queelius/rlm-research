---
title: Sparse-head infrastructure recovery for composed-RL window 03
date: 2026-09-10
status: prospective_before_recovery_gpu_execution
---

# Question

Can the exact failed window-03 update be completed by removing logits that have zero
dependency in the frozen loss and enlarging the inadequate infrastructure deadline, without
changing its episodes, credit, weights, optimizer state, RNG, or update count?

# Fixed recovery

The original attempt remains immutable. This additive attempt authenticates its exact
11-episode/154-turn group, generation, original recipe, and Adam1 checkpoint. It makes two
operative infrastructure changes: Qwen3's language-model head receives only each current
action's predecessor positions, and the one-update optimization cap is 1,800 seconds rather
than the failed 240 seconds. The old recipe stays pinned as the scientific recipe; these two
post-failure changes have their own source and campaign identity.

Stage 1 has a 900-second cap and cannot construct or step an optimizer. It compares full and
sparse outputs on the shortest frozen turn, using the turn's actual advantage, and requires
maximum log-probability error <=0.005, loss error <=0.002, relative LoRA-gradient L2 error
<=0.01, and gradient cosine >=0.99995. It then requires a finite sparse forward/backward on
the frozen longest 8,192-token turn and records time and CUDA peaks. A CPU tiny-Qwen fixture
checks the same algebra first.

Stage 2 runs only after both gates pass. It re-authenticates the old native export, reloads
the exact checkpoint-1 adapter, Adam moments, and RNG, processes the unchanged turns in their
original order with identical episode/turn/action weighting and TIS/PPO numerics, and may
commit exactly update 2. Every turn records sequence length, selected positions, and elapsed
forward/loss/backward time. No evaluation, recollection, refill, truncation, regrouping,
micro-update, or checkpoint selection is included.

The owner is bounded to 3,000 seconds: qualification <=900, total work <=2,700 with training
<=1,800, owned cleanup through 2,970, and a 30-second outer margin. Failure preserves Adam1.
Passing establishes numerical agreement within the declared tolerance, not bitwise identity.
The earlier 276-second extrapolation is only a rough dense-trainer workload proxy; sparse
projection can materially change seconds per token. The 1,800-second cap is pragmatic, not a
runtime guarantee.

# Decision

Promote checkpoint 2 for a separately approved readout only if qualification passes, one
actual Adam step is authenticated, all distribution guards pass, and the atomic checkpoint
binds the exact old group/generation. Otherwise retain checkpoint 1 and classify this exact
group as infeasible under the qualified recovery. Any smaller group or changed credit rule is
a new campaign.

