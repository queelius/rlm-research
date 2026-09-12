# Conditional fixed-checkpoint evaluation interface

Evaluation is permitted only when `outputs/attempt-001/RESULT.json` has status
`COMPLETED_FOUR_UPDATES`, exactly four optimizer steps, primary checkpoint
`checkpoint-0004`, and all four `STEP_COMMIT.json` identities/files revalidate through
`training.result_for()`. Use only `checkpoint-0004/EVAL_BINDING.json`: the root is the saved
procedural adapter on Qwen3-4B-Instruct-2507, while the child remains that exact base model with no
adapter. Earlier steps are diagnostic and never candidates.

The final comparison, if separately approved and sealed, is base versus checkpoint4 on the16
untouched heldout records with two prospectively fixed repeats each. Preserve original JSON bytes,
public queries, exact official scorer, renderer, depth1, cumulative six returned-turn cap,
temperature0.5, output cap2048, no retry, and identical seeds across policies. Report C/W/U,
official exact/continuous scores, root/child calls, tokens, unknown usage, and context clusters. Do
not tune or select using heldout results and do not call these records unseen in base pretraining.
