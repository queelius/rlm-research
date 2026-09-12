# Fixed-baseline final-decision RL readout

COMPLETE_PAIRED_AUDIT

held: cp32 25/32 correct (32 available); RL 22/32 correct (32 available). 0 wins, 3 losses among 32 available pairs; 0 unknown. 16 context units, 16 complete paired contexts.
Clean-target/copy taxonomy: cp32 {'clean_target_copy_failure': 5, 'exact_after_clean_target': 25, 'no_clean_target_and_wrong_final': 2}; RL {'clean_target_copy_failure': 8, 'exact_after_clean_target': 22, 'no_clean_target_and_wrong_final': 2}.
Physical returned calls/tokens: cp32 64 / 70634 input + 20739 output; RL 66 / 73829 input + 23170 output. Unknown-cost calls 0 / 0. Owner seconds 424.32 / 396.36.

Training cost is separate: 43.74s science, 56.20s owner, one optimizer step.

Two fresh decoding seeds on the same16 exposed contexts, both fixed models newly evaluated. No new training or independent dataset; repeated seeds are not independent contexts. Saved earlier training cost is context, not newly spent compute.

Scores and native token decoding are recomputed; causal mapping/failure classification and clean-observation definitions reuse reviewed helpers. No generated program was executed. No checkpoint, example or threshold was selected from this readout.
