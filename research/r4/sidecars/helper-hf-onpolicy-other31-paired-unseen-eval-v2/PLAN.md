# Conditional paired repaired-run evaluator

Preserve V1 and the fixed unseen256 schedule. Reuse its full paired checkpoint,
probability, optimizer, binding and native-service qualification. The only source
semantics change is explicitly authenticated reuse of the failed run's exact128
HF actions; this is not new sampling or historical vLLM probability reuse.

1. Add a thin V2 facade/owner with one real collector build and reuse-rejection
   fixture. Pin the repaired training READY and the entire source closure.
2. MAIN reviews and may launch each eligible branch (64 calls, 600 owner / 700
   external seconds). Neither evaluation can start unless BOTH branch updates
   and all64 replay groups, source bytes and branch initial states authenticate.

No GPU launch, data selection, changes to previous source/output, or cap changes.
