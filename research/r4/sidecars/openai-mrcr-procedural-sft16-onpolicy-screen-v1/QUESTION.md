---
schema: cp16-g4-screen-question-v1
question: Does less SFT retain the learned procedure while restoring within-context reward variation?
status: CPU preparation only, MAIN sole launcher
selected_checkpoint: original continuation step16, predetermined midpoint
control: completed fixed cp32 T.5 same first8 TRAIN x G4
sampling: original paired seeds202609200000..31, T.5, top_p1, top_k-1, min_p0
caps_seconds: {science: 900, owner: 1100, external: 1200}
optimizer_steps: 0
---

All32 trajectories use exactly the original eight training contexts, prompts, ordered tools and initial token IDs, four paired seeds each. The only intended model condition change is the predetermined intermediate checkpoint16 versus checkpoint32. This is an adaptive research question selected after cp32 collapsed, not outcome-selection among cp16 candidate runs. No model queried cp16 before this choice.

The actual checkpoint16 alias, adapter hashes, original STEP_COMMIT, Adam16 and RNG are authenticated. Its immutable training EVAL_BINDING correctly says step16 and source-run fixed_primary_step32: this study does not rewrite that historical primary. The fixed zero-LoRA child transport and six total root+child action cap are unchanged; no child update or forced delegation. Terminal-strip-disabled hooks are unchanged, including reasoning newline semantics. Raw exact is primary; unavailable is not wrong. Mixed exact-reward groups and procedure/stdout/final-copy distinctions determine whether any future RL question is useful; zero variance means no update, never resampling until success.

No heldout input, new training, optimizer, or model selection is performed. A train-only32 episode screen cannot establish generalization or a benefit from recursion. cp32 control is reused from its complete qualified same-template/sampling run, with separate service/cache histories and observed cost disclosed.

