# LR10x checkpoint-3 saturation escape: proposed paired comparison

This is a proposal only. It does not authorize training or evaluation selection.

Question: can the 128 saved, checkpoint-3-on-policy update-4 actions produce a useful fourth
update when all 32 within-question RLOO groups have zero contrast?

Use three branches from the exact LR10x checkpoint-0003 state, adapter, AdamW state, and RNG:

1. unchanged checkpoint-3 policy (no fourth optimizer call);
2. detached leave-current-question-out (`other31`) reward baseline on the already saved 128 actions;
3. momentum-only control: run the same carried AdamW fourth `step()` with an exactly zero gradient,
   recording whether optimizer momentum/decay alone changes parameters. Weight decay remains zero.

The other31 baseline for each action is the mean reward among the other 31 questions (124 actions),
detached from policy outputs. With the frozen update-4 rewards, 120 correct actions receive
`+0.0645161290322581` and eight wrong actions receive `-0.967741935483871`; all 128 become nonzero.
Use sequence-sum log probability and the same fixed denominator 128. Recompute current selected-token
log probabilities from checkpoint 3 and require equality with saved behavior log probabilities under
the original tolerances before any update. Do not recollect or change seeds.

Both optimizer branches must start from bit-identical checkpoint-3 adapter/Adam/RNG snapshots. The
zero-gradient branch is a mechanics control, not a learning baseline; if it changes weights through
carried moments, compare the other31 branch against both it and unchanged checkpoint 3. Save full
parameter deltas, optimizer step/state, gradient norm, qualification, and immutable source hashes.
Evaluate all three on the same fixed256/T0 panel only after commits, without checkpoint selection.

Interpretation: this tests escape from reward-contrast saturation using a different standard
action-independent baseline. It does not isolate learning-rate effects, and reuse of saved actions is
valid only for the exact checkpoint-3 policy after the probability-equality gate passes.
