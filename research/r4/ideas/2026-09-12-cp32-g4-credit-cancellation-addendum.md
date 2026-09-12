---
schema: g4-credit-cancellation-addendum-v1
supersedes: the claim that identical first actions plus clean stdout automatically makes paired credit masks informative
original_design_sha256: 3e6415c7392acbe02520db99042525aac0ea64d592b2571aec2a4488756f042e
status: design correction, no optimizer admission
---

# Identical first-action credit cancels within G4

MAIN identified an important algebraic limitation in the proposed paired masks. G4 RLOO advantages sum to zero. If all four trajectories share the same first prompt/action, their initial HF per-token gradients are identical. Under the proposed detached token-TIS objective, if their first-turn native logps are also identical, their first-turn weights are identical. The complete group's first-turn gradient is therefore exactly zero, regardless of whether that action is included in the mask.

Consequently, mixed final-copy outcomes following identical first actions may produce the same all-root and final-only gradient. Such a pair would not isolate credit assignment and should not consume two optimizer/readout arms. Tiny native/HF numerical differences are not a substantive mechanism. This cancellation does not generally hold for full-trajectory importance weights that vary with later actions; that is a different objective and must not be conflated with token-TIS.

Before any paired optimizer admission, compute/compare the two saved gradient vectors at the same initial model: norms, difference norm relative to each norm, cosine, and which earlier action terms fail to cancel. If effectively identical, prefer one predeclared useful RL update followed by fresh G4 and the fixed held/long readouts, with mask comparison retained as a CPU/gradient diagnostic. A genuinely different earlier action can make the paired experiment informative, but final-only is then knowingly omitting procedure-related credit.

The completed cp32/T.5 batch is even simpler: all32 advantages are zero, so neither mask permits an update. Earlier-checkpoint and higher-temperature screens are separately approved diagnostics; no optimizer or heldout-selected training is implied.
