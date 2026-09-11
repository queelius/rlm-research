---
title: Independent sparse-head gradient numerical audit
date: 2026-09-10
status: complete
---

# Result

The original 1% relative-L2 / 0.99995 cosine gate is below measured repeatability for this exact
GPU backward path. Two nominally identical dense passes differed by 1.3781% with cosine
0.99990567. Dense A versus sparse differed by 1.8162% with cosine 0.99983683; dense B versus
sparse was 1.8232% / 0.99983859. All three scalar losses were exactly -0.7070403695 and all 116
selected-action log probabilities were elementwise identical.

Therefore the failed dense-sparse comparison cannot be interpreted as a unique objective-gradient
difference. Accurate CPU float64 reductions also show that the earlier cosine above one was a
measurement defect. They do **not** establish that sparse and dense gradients are mathematically
equivalent: the sparse difference is larger than repeat noise, only two dense repeats exist, and the
execution does not isolate BF16 arithmetic, SDPA/backward kernel nondeterminism, gradient
checkpointing, or changed output shape.

# Independent vector audit

All three persisted vectors were read CPU-only and independently reduced in float64. Checkpoint1's
504 `optimizer_parameter_names`, paired with optimizer first-moment tensor shapes, close exactly to
all 16,515,072 flattened elements. This supports the assumed `named_parameters()` ordering without
loading the model. Per-parameter results are in `AUDIT.json`.

The discrepancy is diffuse rather than one corrupted slice. For dense-repeat the largest parameter
contributes 2.85% of squared difference and the top ten 20.69%; for dense-sparse these are 2.70% and
19.27%. LoRA-B tensors account for 99.38% of dense-repeat and 99.11% of dense-sparse difference
energy. The same families dominate both comparisons, which is compatible with shared backward
numerics, but is not a causal diagnosis.

# Decision boundary

Do not silently relax or retrospectively pass the old gate. A separately versioned exploratory
engineering policy may reasonably require both comparisons below 3% relative L2 and above 0.9995
cosine, plus dense-sparse absolute difference no more than twice dense-repeat, while retaining the
original loss/log-probability gates and the already-finite 8,192-token sparse check. Here the ratio is
1.318 and those declared gates pass. If used, it permits only the exact Adam1-to-Adam2 update on the
frozen failed group; it is not confirmatory equivalence evidence. A fixed checkpoint2 behavioral
readout is still necessary.

A copied-Adam one-vector candidate-delta comparison was considered but not performed: AdamW's
per-coordinate normalization can amplify tiny-gradient differences, and choosing a parameter-space
tolerance after seeing the gradients would add another post-hoc gate without answering behavior.
The exact one-update execution plus precommitted protected readout is the more direct bounded
discriminator.

# Closure

- diagnostic owner: `5f9dcaa9c7a4292b56b44322303e5414b9a8a48c087a3098957c07dea95dba28`
- parent exit: `e9ebcc7871238cf08d37ec4024d84503b8a17639b8f319d1f9df759c4fe313db`
- producer result: `cac8842d47cf2189d465d4589dbf0228255ae66764683e5e383178355c42434f`
- independent audit: `f7e8c210da7d9f99b5c2f8c4c80e13ade31a1bb66f2dc69590fd912c536b390e`
- optimizer steps: zero; owner and parent both report release and no GPU process after exit.
