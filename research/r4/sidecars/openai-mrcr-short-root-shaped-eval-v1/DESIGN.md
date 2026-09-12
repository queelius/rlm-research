---
schema: openai-mrcr-shaped-root-heldout-eval-design-v1
status: CPU_PREPARATION_ONLY
gpu_launch_authority: MAIN_ONLY
optimizer_steps: 0
---

# Fixed held16 comparison after one shaped-root update

The unchanged released root and the exact fixed step-1 root checkpoint each receive one rollout on
the same 16 disjoint short-MRCR heldout contexts and seeds. Both use the same released base child,
temperature 0.5, external `/context.json`, maximum 2,048 tokens/action, and six total root/child
turns. There is no newline or output repair.

Primary comparison is paired raw exact. Raw official similarity, the prespecified `>=0.90` band,
and `0.5*band + 0.5*exact` are retained as diagnostics. Unavailable coordinates remain unavailable.
At least two updated-only raw-exact wins, no losses, and 32 authentic available endpoints is the
frozen exploratory positive screen. Anything weaker retires this checkpoint as a positive endpoint,
not the entire reward direction. The training code did not measure post-update likelihood shift;
gradient norm and adapter delta distinguish a zero/failed update, but do not quantify probability
movement.

The motivating near-successes used 18,683--20,000-character broad tool observations, three of them
truncated. A higher exact score would therefore be a root-procedure result, not evidence of learned
decomposition or efficient retrieval. Observation size, truncation, tool exceptions, and selected
assistant-turn correctness remain required interpretation diagnostics.
