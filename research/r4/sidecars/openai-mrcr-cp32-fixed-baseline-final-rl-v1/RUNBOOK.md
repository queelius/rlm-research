# Fixed-baseline final-decision REINFORCE: one conditional candidate

MAIN-only admission. CPU preparation does not authorize a GPU or optimizer. The source batch is the completed cp32/T.5 G4 screen: eight contexts, 32 available trajectories, 28 exact, four incorrect from one duplicated newline-copy failure. All 32 actual final actions are retained, not new samples or newly varied behavior.

Question: can one reward-weighted conditional-terminal update improve exact answer execution while retaining the learned retrieval procedure? Loss is `-sum_i[(r_i-.5) sum_t min(exp(logp_HF-logp_native),2) logp_HF]/32`, using detached weights. It is a prospectively biased token-TIS surrogate, not exact sequence importance sampling. Final conditional states are frozen; shared LoRA changes can nevertheless alter earlier procedure generation. There is no mixed-group admission gate for this new objective and no answer rewriting, gold-target replacement, unlikelihood objective, or tail-only loss.

Run only under MAIN's shared-lock wrapper with an external 1200s timeout:

```
/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-cp32-fixed-baseline-final-rl-v1/owner.py verify
/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-cp32-fixed-baseline-final-rl-v1/owner.py run
```

Caps are 900s science, 1100s subprocess owner plus bounded cleanup, 1200s external. A single HF model load, no native service, no generation calls. The old comparable token-TIS gradient run took about 106s for 15,602 action tokens; this candidate has 10,420 final tokens but adds negative-token-component gradient diagnostics. This is a cost estimate, not a guarantee. Probability support/replay failure, zero/nonfinite gradient, OOM or time cap is a valid no-qualified-update outcome; no recollection or fallback.

`outputs/attempt-001/checkpoint-0001` is the only prospective endpoint. `INITIAL.json` authenticates every actual loaded adapter tensor against the cp32 safetensors. `PRESTEP_LOGPS.json` preserves all selected HF log probabilities and detached weights; `PRESTEP_QUALIFICATION.json` retains conditional-sequence diagnostics without relabeling them full-RLM IS. `gradient/REPLAY.json` records every no-grad/grad comparison at 1e-5 per token and 1e-4 summed action, objective and norm. No Adam object exists until all 32 pass. The one fresh AdamW has LR1e-5, weight_decay0, betas(.9,.999), eps1e-8, clip1; its state counters must equal one. Initial tensors/RNG, saved gradients, final optimizer/RNG, state, binding and commit are preserved.

Expected versus actual locality: the wrong final is mostly a correct 411-character answer plus two extra linefeeds. The sampled token containing the error also contains the gold trailing spaces. All its final tokens remain in the loss. Negative-sample body/whitespace/EOS parameter-gradient tensors and their norms are saved separately, then added to the same total gradient. These norms measure actual local gradient contributions, not entropy or independent causal effects. Post-step conditional log-probability changes are diagnostics, never rollout success.

Conditional successor interface: require RESULT UPDATED, owner complete/reaped, one Adam step, all 32 replay passes, actual cp32 initial binding, nonzero finite adapter delta, and every STEP_COMMIT/state/source hash. Use the new root alias/path from EVAL_BINDING; child remains zero-loss/disabled in evaluation. Evaluate the fixed held and long panels with the same terminal-fidelity hooks and caps and their qualified cp32 reference. Do not select a checkpoint on those readouts. An improvement would be exploratory fixed-batch terminal-policy learning, not learned retrieval, recursion, or new trajectory diversity.
