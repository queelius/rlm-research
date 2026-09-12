# Fixed LR dose arm: actual checkpoint qualified

LR1e-4 completed one step from original cp32 in33.2515seconds science. Adapter delta L2 is0.404606208 versus0.040460656 for LR1e-5. The new endpoint passed full original-initial-tensor,12-action replay/20-exact-skip, saved-gradient/Adam-moment, RNG and state/commit/binding checks. No accuracy condition enters qualification.

Old and new PRESTEP_LOGPS.json and PRESTEP_QUALIFICATION.json are byte-identical: same HF chosen log probabilities, detached TIS weights and probability qualification on the frozen native batch. The new gradient replay receipt is not bitwise identical; reported preclip gradient norm is24.299283981 versus24.309085846. Both satisfy the same original replay tolerances. This is a nominal learning-rate-only recipe comparison, not a claim of perfectly identical floating-point backward execution. No rerun or posthoc recipe change was made.

Endpoint result/state/commit/binding hashes are pinned by the new evaluator READY9373367ef6c6f7441d5415a4f852ce86b42c0e0e8d101ab75dd983c1172fc193. Checkpoint qualification SHA c950abc930ae465b7b45aa9e06e571aa0da4b832ac20feec931a8da80565a031. Fixed training32 and exposed held32 are planned regardless interim scores; no additional optimizer is authorized here.
