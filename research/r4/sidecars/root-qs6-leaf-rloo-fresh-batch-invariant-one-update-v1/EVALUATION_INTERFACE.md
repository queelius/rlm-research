# Fixed checkpoint-0001 evaluation handoff

Evaluation is eligible only when `RESULT.json` is `UPDATED` with exactly one optimizer step and
points to `checkpoint-0001`; the complete `STEP_COMMIT.json` inventory verifies; state records the
exact c32 start, frozen dataset/masks/qualification and passing gradient-path replay hashes; AdamW
serializes step 1; and `EVAL_BINDING.json` changes only the fixed child while preserving QS6 root and
campaign metadata.

Evaluate checkpoint-0001 only on the exact frozen new256 schedule from
`helper-unseen-generalization-c32-baseline-v1`: 64 batch-of-4 native calls, temperature 0, identical
seeds and ordered schemas, 600-second owner / 700-second external cap. Compare to the existing c32
baseline with missing outcomes separate. This adaptively reused panel is a bounded downstream
readout, not pristine generalization or a comparison to the 32-question B4 HF reference.
