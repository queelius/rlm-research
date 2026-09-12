# Fresh48 fast one-update independent audit

The repaired run is a genuine qualified update: 48/48 differentiable replay rows passed with zero token and sequence error, prestep ESS was 45.449/48, the AdamW state is exactly step 1, and only child action tokens contribute to loss. Training took 36.309s in the trainer and 43.101s externally.

The fixed256 readout is **120/128 TREC + 112/128 AG News = 232/256**. Against c32 (231/256), exactly one label changed (`tee8c28875d38a31`), producing one TREC win and no loss. Against the separate four-step reference, all **256/256 labels are identical**. Therefore this is not evidence of a unique RL gain; it is one valid update whose adaptive, research-exposed readout lands on an already observed prediction vector.

Collection cost is separate from training: the reused never-updated batch made 48 native calls, 60576 prompt tokens, 11901 completion tokens, and 369.655 summed request-seconds. Native collection owner time was 166.766s; HF likelihood recovery was 16.827s; the update was not recollected. Evaluation used 64 calls, 64962 tokens, 55.398 summed request-seconds, and 110.109s externally.

RNG evidence records master/Python/Torch/CUDA seed 202609121401 and the explicit NumPy legacy modulo seed 745658489. Raw fixed256 completion IDs, request bodies, ordered IDs, and the full source collection request/response hashes were independently checked. The panel is unseen only relative to verified c32 optimization inputs/new32—not base pretraining—and has been repeatedly used for research decisions.
