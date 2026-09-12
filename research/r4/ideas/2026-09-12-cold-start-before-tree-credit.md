---
schema: research-idea-v1
id: cold-start-before-tree-credit
created_utc: 2026-09-12T16:11:00Z
status: evidence_informed_followup_not_architecture_claim
priority: high_after_short32
related_questions: ["rq:controller", "rq:rl-effective-feedback"]
gpu_admitted: false
---

# Teach a usable procedure before judging recursive RL

Our long-conversation pilot returned no exact answer in32 trials. The new
selection API produced only9 finish-consistent finals in48 episodes. These are
distinct failures; neither establishes that learning decomposition is impossible.

## Relevant primary account

Kim and Ahmad report that their small RLM needed a supervised warm-start before
RL, and that using too much of their RL corpus for SFT reduced exploration.
Their recursive objective shares a policy across roles and averages child
contributions per parent. Their task uses judged evidence quality, not our exact
retrieval reward, and their main run used eight H200s.
[Authors' May13 report](https://www.alphaxiv.org/blog/reinforcement-learning-for-rlms).

The cached official SkyRL source is commit
`955c3e23bf8939b28a9d6c424308a762dcb8a2e7` (Apache2, clean worktree at review).
Its current sample shell config is not the blog's exact run: it names a2B SFT
model, batch4 and four training GPUs. The inspected generator coalesces child
steps; that alone does not establish exactly how the trainer weights them.
Do not claim a reproduction or inherit its mathematical claims without checking
the full training path. No external code was executed in this review.

## Local decision and smallest informative sequence

Finish the short32 base calibration. If retrieval is weak, use the already
prepared fixed4-update, all32-demonstration procedural SFT dose (600s training
cap, checkpoint every update). Its teacher solves32/32; that is not a model
result. Test the fixed endpoint on training conversations before consuming the
16 heldout conversations. Keep child weights fixed to isolate root learning.

If the root becomes competent but its sampled answers are all identical, do
not increase temperature indefinitely or reward arbitrary overlap. Diagnose
whether a harder, separately frozen training cohort supplies genuine success
and failure. Full32 warm-start coverage is an explicit local choice, not a
reproduction of the authors' small-subset recipe. A lower-dose/subset comparison
is useful only if actual post-SFT diversity collapses.

If SFT still cannot execute the procedure, inspect action and terminal errors
separately. If it executes correctly and transfers, then examine when semantic
helper calls are useful. MRCR retrieval often has a deterministic Python solution;
success there alone would not show learned delegation or depth selection.

## Reference receipts

Retrieved/reviewed September12. Source URLs are the authors' blog and
https://github.com/NovaSky-AI/SkyRL/tree/955c3e23bf8939b28a9d6c424308a762dcb8a2e7/examples/train/rlm.
Local generator SHA256 `377a4f5303e579d15c8bbcaffd19422b4563aecc1f5a37bc24b488d2101269dc`;
sample shell SHA256 `a402a4301193fe9b16e6c83c16ab9cacde0dcaa4d4341f7ef9519ec15ba58895`.
Blog is an author experiment account, not a controlled result for our system.
