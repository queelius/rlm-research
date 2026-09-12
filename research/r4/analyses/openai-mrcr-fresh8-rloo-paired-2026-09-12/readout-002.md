# Fresh8 RLOO paired native readout

COMPLETE_PAIRED_AUDIT

held cp32: 25/32 correct; 32 available, 0 unavailable. Physical 64 returned/0 errors/0 start-only/0 orphan returns; 70634 input + 20739 output tokens; 0 unknown-cost calls; owner 424.32s.
Copy/retrieval taxonomy: {'clean_target_copy_failure': 5, 'exact_after_clean_target': 25, 'no_clean_target_and_wrong_final': 2}; stops {'agent_completed': 32}.
held fixed_baseline_RL: 22/32 correct; 32 available, 0 unavailable. Physical 66 returned/0 errors/0 start-only/0 orphan returns; 73829 input + 23170 output tokens; 0 unknown-cost calls; owner 396.36s.
Copy/retrieval taxonomy: {'clean_target_copy_failure': 8, 'exact_after_clean_target': 22, 'no_clean_target_and_wrong_final': 2}; stops {'agent_completed': 32}.
held updated: 25/32 correct; 32 available, 0 unavailable. Physical 64 returned/0 errors/0 start-only/0 orphan returns; 70634 input + 20739 output tokens; 0 unknown-cost calls; owner 408.40s.
Copy/retrieval taxonomy: {'clean_target_copy_failure': 5, 'exact_after_clean_target': 25, 'no_clean_target_and_wrong_final': 2}; stops {'agent_completed': 32}.
RLOO vs cp32: 0 wins/0 losses in 32 available pairs; 0 unknown. Contexts improved/worsened 0/0, 16/16 complete.
RLOO vs fixed_baseline_RL: 3 wins/0 losses in 32 available pairs; 0 unknown. Contexts improved/worsened 2/0, 16/16 complete.

long cp32: 10/16 correct; 16 available, 0 unavailable. Physical 32 returned/0 errors/0 start-only/0 orphan returns; 34352 input + 11431 output tokens; 0 unknown-cost calls; owner 252.20s.
Copy/retrieval taxonomy: {'exact_after_clean_target': 10, 'clean_target_copy_failure': 5, 'no_clean_target_and_wrong_final': 1}; stops {'agent_completed': 16}.
long updated: 10/16 correct; 16 available, 0 unavailable. Physical 32 returned/0 errors/0 start-only/0 orphan returns; 34352 input + 11431 output tokens; 0 unknown-cost calls; owner 238.77s.
Copy/retrieval taxonomy: {'exact_after_clean_target': 10, 'clean_target_copy_failure': 5, 'no_clean_target_and_wrong_final': 1}; stops {'agent_completed': 16}.
RLOO vs cp32: 0 wins/0 losses in 16 available pairs; 0 unknown. Contexts improved/worsened 0/0, 16/16 complete.

fourneedle cp32: 10/16 correct; 16 available, 0 unavailable. Physical 31 returned/0 errors/0 start-only/0 orphan returns; 33106 input + 10880 output tokens; 0 unknown-cost calls; owner 264.71s.
Copy/retrieval taxonomy: {'exact_after_clean_target': 10, 'clean_target_copy_failure': 3, 'no_clean_target_and_wrong_final': 3}; stops {'agent_completed': 16}.
fourneedle updated: 11/16 correct; 16 available, 0 unavailable. Physical 31 returned/0 errors/0 start-only/0 orphan returns; 33319 input + 11195 output tokens; 0 unknown-cost calls; owner 237.69s.
Copy/retrieval taxonomy: {'exact_after_clean_target': 11, 'clean_target_copy_failure': 3, 'no_clean_target_and_wrong_final': 2}; stops {'agent_completed': 16}.
RLOO vs cp32: 1 wins/0 losses in 16 available pairs; 0 unknown. Contexts improved/worsened 1/0, 16/16 complete.

Training separate: 33.24s science, 46.23s owner.

Different weights: native token equality is descriptive, not clamp-only causality. Short uses the new decoding-replica seeds for every arm. Batch and reward estimator both differ between RL recipes. All panels are research-exposed; base pretraining unknown. Repeats are clustered within sixteen contexts per panel. Mapping, stop/failure rules and clean-observation taxonomy reuse the reviewed collector; scores, native token decoding and costs are recomputed.
