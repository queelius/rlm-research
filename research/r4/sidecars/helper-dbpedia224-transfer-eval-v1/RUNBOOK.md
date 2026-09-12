# DBpedia-224 transfer evaluator

Run each READY command separately under MAIN's shared GPU lock and private credential environment.
Each owner has a 700-second internal cap and 800-second external cap. All four checkpoints were fixed
before any query on these 224 records and must be reported; neither RL seed is selected by outcome.

After all terminals, run `compare.py` CPU-only with CUDA hidden. This is a new locally evaluated
official-test panel in a different source domain and 14-label vocabulary, but still short-text
classification. It is not broad reasoning, planning, recursion, or evidence of no base pretraining.

