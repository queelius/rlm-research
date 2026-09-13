# Candidate-local credit

On one qualified frozen 16-question G4 native decision-vector batch, apply one LR 1e-4 update from a
fresh, seeded, zero-B LoRA. Each candidate's boolean-token likelihood receives that candidate's binary
correctness RLOO advantage, scaled by `1 / candidate_count` and the fixed 64-episode denominator.

This is paired with the response-joint arm using identical actions, initialization, optimizer, masks,
and denominator. It is a biased token-TIS surrogate, not an unbiased sequence-policy-gradient claim.

