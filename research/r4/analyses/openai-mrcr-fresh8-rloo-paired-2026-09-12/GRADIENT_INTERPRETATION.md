# What drives this saved update?

The fresh RLOO gradient is much larger before clipping (24.309 versus 0.004436 for the earlier fixed-baseline batch), but it is clipped to approximately1 before Adam. The realized adapter delta is0.040461; gradient norm is not an update-size or rollout-gain measurement.

After correctly applying the clip factor to the saved negative components, their signed projections onto the full gradient are approximately9.16% whitespace,5.38% EOS and0.00054% body/content tokens. The inferred positive-reinforcement residual supplies85.45% of that projection and has cosine0.9925 with the total. These are vector projections, not causal fractions of an Adam update.

All three successful finals have their largest chosen-token surprise at the penultimate token representing the required two ASCII spaces. HF chosen log probabilities are approximately-2.129,-2.353 and-0.469. The corresponding failures include an added newline, early EOS before those spaces, or extra newlines. The negative content-token gradient is tiny relative to whitespace/EOS.

This supports an exact-copy/termination-boundary interpretation of the available learning signal, not new evidence of retrieval learning or final-word rewriting. Positive body/whitespace/EOS parameter gradients were not saved separately: token likelihoods identify the visible decision contrast but do not prove an exact per-token allocation of the positive gradient. The eight literal-selector failures have zero RLOO advantage and contribute no gradient.

The saved-step scaling diagnostic in GRADIENT.json holds the realized full update transformation fixed. It can produce large mutually cancelling component norms and must not be read as the counterfactual Adam update after removing a component. No backward pass, optimizer or model inference was rerun.

Source: the immutable GRADIENT.json and CPU_READY.json in this directory. This interpretation is additive; it does not modify their sealed evidence.
