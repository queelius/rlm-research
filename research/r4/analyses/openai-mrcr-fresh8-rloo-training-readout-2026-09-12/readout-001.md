# Fresh8 RLOO: in-sample behavioral diagnostic

COMPLETE_PAIRED_AUDIT

Exact: cp32 7/32 → RLOO 17/32; available 32/32; unavailable 0/0. 10 wins/0 losses, 0 unknown pairs. 17/32 identical native paths.

| Context | cp32 G4 | RLOO G4 | Paired net |
|---|---|---|---|
| omrcr-next-fa62a38bf5881860a77e | 0000 | 0101 | 2 |
| omrcr-next-83e8a79356c89d99db7f | 0100 | 1111 | 3 |
| omrcr-next-4e5fbf922e52f33584a7 | 0000 | 0000 | 0 |
| omrcr-next-969a7a61b93c8afa176a | 0000 | 0000 | 0 |
| omrcr-next-3bdc3e44003cf70afba9 | 1111 | 1111 | 0 |
| omrcr-next-64266bb0bf4dd84060f3 | 0001 | 1011 | 2 |
| omrcr-next-0e42ccab3de2dc127f09 | 0010 | 1111 | 3 |
| omrcr-next-ff6be6cbca8e5d4571b5 | 0000 | 0000 | 0 |

U denotes unavailable/unattempted, never incorrect.

cp32: copy types {'exact': 7, 'edge_whitespace_difference': 17, 'no_clean_target_evidence': 8}; stops {'agent_completed': 32}.
Physical: 66 returns, 0 errors, 0 start-only, 0 orphan returns; 69717 input + 21111 output tokens, 0 unknown-cost calls; owner 404.60s.

RLOO: copy types {'exact': 17, 'no_clean_target_evidence': 8, 'edge_whitespace_difference': 7}; stops {'agent_completed': 32}.
Physical: 65 returns, 0 errors, 0 start-only, 0 orphan returns; 68270 input + 20976 output tokens, 0 unknown-cost calls; owner 387.78s.

Changed paths: 15; full per-pair copying/action/observation fields in JSON, without answer text.
Training separate: 33.24s science / 46.23s owner.

Original optimized training batch and same decoding seeds: in-sample diagnostic, not transfer or independent replication. All32 retained, including20 zero-advantage trajectories. Native token decoding, official scores and costs recomputed; causal/clean-observation taxonomy reuses reviewed helpers. Eight context clusters, not32 independent tasks. Changed weights prevent clamp-only causal attribution; no automatic optimizer admission.
