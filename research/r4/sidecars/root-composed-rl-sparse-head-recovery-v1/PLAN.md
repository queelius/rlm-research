# Execution plan

1. Authenticate the old group, generation, recipe, checkpoint-1 adapter/Adam/RNG, and native replay.
2. Run the no-step full-versus-sparse and longest-turn GPU qualification.
3. Only on a passing qualification, run the exact group once from Adam1/RNG1 and commit update 2.
4. Verify the atomic checkpoint, retain all timing/memory/correction receipts, and release the owned process group.
5. Do not evaluate or continue later windows without a new reviewed decision.

