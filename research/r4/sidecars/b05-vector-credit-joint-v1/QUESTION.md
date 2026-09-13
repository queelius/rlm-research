# Response-joint credit

On the exact same qualified 16-question G4 native decision-vector batch and fresh zero-B LoRA seed as
the local arm, apply one LR 1e-4 update. Every candidate's boolean-token likelihood receives the
response mean-candidate-correctness RLOO advantage, with the same `1 / candidate_count` scaling and
fixed 64-episode denominator.

Only credit assignment differs from the candidate-local arm. This is a biased token-TIS surrogate,
not an unbiased sequence-policy-gradient claim.
