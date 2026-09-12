# Conditional step-four evaluation interface

An evaluator may bind only after `outputs/attempt-001/RESULT.json` reports exactly four completed
optimizer steps and authenticates checkpoint-0004 plus its STEP_COMMIT, state, Adam step4, RNG, and
EVAL_BINDING. The frozen AG News heldout256 is then evaluated at temperature zero alongside c32 and
the reference T1 step-four policy on identical batch-four requests. No checkpoint selection.
