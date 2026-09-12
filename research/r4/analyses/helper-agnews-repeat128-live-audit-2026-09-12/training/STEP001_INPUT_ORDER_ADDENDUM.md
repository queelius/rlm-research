# Paired step1 training-input audit

Compared actual128-row HF dataset order, packed grammar masks, saved backward capture, Adam parameter groups/layout and RNG. Masks identical: 128/128. Capture equality counts: {'group_id': 128, 'reward': 128, 'advantage': 128, 'importance_ratio': 128, 'sequence_loss_over128': 128}. Maximum current-policy forward logprob difference: 0.0. Optimizer groups equal: True; prestep receipt equal: True; poststep RNG byte-identical: True.

The exact reused trainer traverses the dataset in its saved order, with no shuffle and denominator128. Moment deltas are reported in JSON; this is not a backward-kernel replication.

Paired randomization and identical forward loss do not imply bitwise-identical backward/Adam updates. No input, mask, advantage, order or optimizer-configuration change was found in these artifacts. Floating-point backward/reduction variation is consistent with the evidence, not independently isolated or proven. No model reselection, rerun, gate change or causal attribution to a specific kernel.
