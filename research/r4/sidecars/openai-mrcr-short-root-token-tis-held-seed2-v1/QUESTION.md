---
schema: mrcr-token-tis-held16-seed2-question-v1
status: prospectively_frozen_cpu_ready_only
launch_authority: MAIN
optimizer_steps: 0
episodes_per_arm: 16
arms: [base, lr1e-5, lr1e-4]
seed_range: [2026091900, 2026091915]
owner_cap_seconds_each: 650
external_cap_seconds_each: 700
---

# Does the near-null token-TIS held-context result repeat under fresh decoding seeds?

The first fixed held-context block produced 0/15 raw-exact available answers for the base and
low-dose policies and 1/15 for the high-dose policy, with the same context unavailable in all
three arms. The single high-dose exact answer used broad context dumping and copying rather than
successful programmatic retrieval. Those results do not support selecting the high dose.

This replication fixes the same 16 held contexts, original task prompts and rendered prefixes,
Qwen3-4B base plus the two already-committed independent token-TIS step-one adapters, temperature
0.5, maximum 2,048 tokens per response, and six total root-plus-child turns. It changes only the
paired seed block to 2026091900--2026091915 and the resulting coordinate IDs. Every arm runs all 16
coordinates; the prior successful coordinate is not isolated or favored.

Primary readout: paired raw exact, with unavailable outcomes kept separate. Diagnostics retain raw
official similarity, similarity at least 0.90, broad-dump/copy mechanism evidence, calls, tokens,
and total-turn compliance. This is repeated decoding on an already exposed exploratory panel, not
new training, a best-dose comparison, learned retrieval, or independent-context generalization.
