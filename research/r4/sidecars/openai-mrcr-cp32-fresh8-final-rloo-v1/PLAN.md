# Fresh8 final-only RLOO implementation plan

Goal: one fixed LR1e-5 update from original cp32 using the completed fresh8 native batch, not the earlier fixed-baseline checkpoint.

Approved scope: 8 groups × 4 trajectories, all 32 in the denominator. A=(reward-group mean)*4/3. Three mixed groups yield 12 nonzero finals; 20 zero advantages skip all gradient work exactly. No unknown nonzero final may be dropped. Native actions, prompts and log probabilities remain unchanged; no gold final answers become training targets.

Files: study.py validates the frozen batch and constants; inputs.py authenticates the reviewed native source; core.py reuses qualified token-TIS/HF/RNG/Adam primitives; train.py streams final-only gradients and saves one committed checkpoint; owner.py retains the finite subprocess lifecycle; prepare.py seals provenance and actual CPU entry; test_train.py tests the real loss/mask/replay path.

1. Implement and CPU-qualify: first test denominator/zero-skip and actual tiny HF replay failure with no optimizer; authenticate all 32 source trajectories and the exact cp32 binding. Save full inputs, probability and effective-mask inventories, gradient, optimizer, RNG, state and commit.
2. MAIN review and admission: no subagent GPU launch. Fixed 900s science/1100s owner/1200s external caps. Conditional fixed endpoint readout, no checkpoint selection.

Limits: conditional terminal objective with shared weights; detached token-TIS cap 2 is deliberately biased, not exact sequence IS. Fresh source contexts are now training data; held/long outcomes are not inputs to this update. Uniform-zero retrieval failures remain in the denominator but supply no learning signal.
