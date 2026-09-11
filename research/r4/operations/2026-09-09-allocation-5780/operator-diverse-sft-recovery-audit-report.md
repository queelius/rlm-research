# Operator-diverse SFT6 additive recovery audit

The infrastructure completion produced 15/24 authenticated fixed-SFT6 finals and 1/24 strict
success, versus the unchanged frozen baseline's 22/24 and 2/24. All 15 available treatment finals
were `Answer: 0`; the sole success was the only zero-gold coordinate. Two treatment RESULT slots are
absent timeouts and seven are recorded native NULLs, retained separately from wrong answers.

Across all 22 recorded treatment episodes, no child call was executed and no reduction used live
returned labels. Six optimizer checkpoints and Adam ordinals are valid, but declining teacher loss
did not transfer to the demonstrated operator loop. This does not support extending the identical
training dose unchanged.

Full independent evidence, missing-data bounds, behavior traces, training checks, costs, and caveats:
`analyses/root-operator-diverse-sft-live-2026-09-10/RECOVERY_REPORT.md`.
