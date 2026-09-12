# Saved-gradient accounting

Fresh total preclip 24.309086; saved postclip 0.99999993; clip factor 0.04113688. Realized adapter delta 0.040460656.
Old fixed-baseline preclip 0.0044359504; distinct source batch and objective.

negative_body: inferred preclip L2 0.0023182015; signed projection on full gradient 0.00001; cosine 0.056464940329791866.
negative_whitespace: inferred preclip L2 6.0931805; signed projection on full gradient 0.09161; cosine 0.365490828576615.
negative_eos: inferred preclip L2 4.1576828; signed projection on full gradient 0.05383; cosine 0.31473598676729375.
positive_residual: inferred preclip L2 20.929989; signed projection on full gradient 0.85455; cosine 0.9925175022205075.

Negative body/whitespace/EOS gradients were saved separately before clipping. Positive residual is inferred from the clipped total and scaled negative components, with FP32 accumulation/rounding. Positive token-subset gradients were not saved. Signed projection shares can exceed one or be negative because vectors cancel. Realized-step scaling allocation holds the full observed Adam/rounding transformation fixed; it is not the counterfactual update after deleting a component and not rollout causality. Chosen logprobs give surprisal, not full-distribution entropy. Old and new batches, advantages and norms differ.
