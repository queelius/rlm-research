# AG native/HF one-step outcome audit

Complete qualified comparison: True.

- c32: 211/256 confirmed correct; 45 observed wrong; 0 unavailable.
- seed1: 212/256 confirmed correct; 44 observed wrong; 0 unavailable.
- seed2: 211/256 confirmed correct; 45 observed wrong; 0 unavailable.

c32 vs seed2 paired: {'both_correct': 211, 'both_wrong': 45}; 256/256 available in both arms.
Training: 128/128 raw actions authenticated, 402/512 available record decisions correct, 6 mixed-count groups.

No heldout improvement in this completed package; do not select training examples using these outcomes.

Source-to-output audit; not independently authored trainer replication.
Training raw wire envelopes authenticated. Evaluation envelopes absent: only saved native token IDs, decoded text, body/response hashes and usage can be audited.
Unavailable outcomes are not wrong answers; costs are observed subtotals with unknown counts.
New AG training128 and fixed disjoint heldout256; research-exposed after readouts, unknown base-pretraining exposure.
Exploratory package bundles domain, data, granularity, reward and dose; no causal-isolation or recursion claim.
