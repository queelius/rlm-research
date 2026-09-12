# Additive paired branch-start repair

Goal: resume the diagnosed V1 failure before either branch, using all128 already committed exact-HF c32 actions, not resampling or changing the scientific comparison. Source V1, its READY and failed output remain immutable.

Root cause: train_pair.run called implementation.restore_rng, but train_four imported save_rng without re-exporting restore_rng from the same sealed rng_receipts module. Bind the already-implemented function and exercise the actual branch-start seam.

Task1: implement repair.py plus one focused real-model branch initialization/update/restore fixture. Authenticate V1 failure, no branch/checkpoint/optimizer, source model snapshot, all32 group commits/actions/masks/RNG, local rewards and both advantage arrays. Copy exact rollout/mask/RNG bytes into a new attempt; reissue only local path/READY commits and an explicit reuse receipt. Load original c32 once, require its tensor snapshot to equal V1, restore that same tensor/RNG start before each fresh AdamW, and replay all32 groups before each one-step update. Keep B4/eager/noKV/eval/dropoutoff/checkpointing, fixed128 denominator, LR1e-5, clipping and probability tolerances unchanged. Caps stay2700/2850 and450/700/1600 by stage; reused collection has zero fresh model calls.

Task2: CPU-seal new READY and additive conditional paired native evaluators, preserving fixed256 inputs/seeds, step1 comparisons and600/700 evaluation caps. MAIN reviews and alone launches. No shared source edits, environment installs, GPU work, new training examples, alternative objective or automatic resume framework.
