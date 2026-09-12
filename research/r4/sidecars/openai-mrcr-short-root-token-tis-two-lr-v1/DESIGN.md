# MRCR token-TIS two-dose update

The failed shaped-root run remains immutable. This additive feasibility/dose probe consumes
the same 24 complete training-only episodes (six G4 groups), including every one of their
74 authenticated root actions and 15,602 native chosen-token log probabilities. It performs
no generation, child inference, environment execution, or heldout query.

The zero-effect rank-8 root LoRA is scored under the original HF implementation at temperature
0.5. Each root token receives detached weight `min(exp(HF - native), 2)`. Finite/nonpositive
log-probability support is required. The loss is the weighted root-token sum times the frozen
G4 RLOO advantage, divided once by the fixed 24-episode denominator. We retain full-trajectory
ESS and concentration as diagnostics, not as an all-or-nothing gate. The tokenwise cap is a
biased surrogate; it is not unbiased sequence IS or proof that native and HF policies agree.

One clipped gradient is computed and serialized. Initial FP32 LoRA parameters and RNG are
serialized before either branch. Each predeclared branch restores that exact initial state,
constructs a fresh AdamW optimizer with weight decay zero, receives the same saved clipped
gradient, and performs exactly one step at either 1e-5 or 1e-4. Both checkpoints are retained;
they are independent step-1 doses, not sequential steps or checkpoint selection. A fixed
10x update-norm/cosine relationship check detects state or optimizer divergence.

All baseline/native token log probabilities and both post-update HF token log probabilities
are persisted by episode and turn. Movement is summarized overall and by frozen advantage
sign. These diagnostics distinguish a negligible update from a procedure failure, but only
the separately frozen held-context evaluation can address task quality.
