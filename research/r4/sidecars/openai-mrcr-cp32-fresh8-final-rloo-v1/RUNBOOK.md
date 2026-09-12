# One fresh8 final-only RLOO update

Question: does relative reward from three mixed fresh-context groups improve exact final copying without harming retrieval? This is not a fixed-baseline replication: both batch and advantage estimator differ. Eight context units, not 32 independent tasks.

Original cp32 is the fixed start. All 32 native trajectories are retained; 7 exact, 25 wrong. Three groups each have one success: advantages +1 for three samples, -1/3 for nine, and exactly zero for twenty. The entire denominator remains 32. The eight literal-selector failures have uniform zero reward and cannot teach retrieval through this RLOO batch.

Only twelve actual bare final actions receive loss, including their sampled EOS tokens. All other actions have zero mask. No forced-final or missing-action substitution; an invalid nonzero final blocks preparation. Native wire responses and source-to-final audit authenticate all 66 returned calls. HF teacher-forces only the twelve credited finals; uniform-zero rows are skipped, not asserted to have passed an HF replay that was never performed.

The qualified prior trainer's full-prefix scorer, temperature .5, BF16 base / FP32 LoRA, SDPA/no KV, nonreentrant checkpointing, disabled dropout, token replay tolerances 1e-5 / sequence 1e-4, clipping 1.0, and fresh AdamW LR1e-5 are unchanged. The detached capped token weights (cap2) are a deliberately biased native/HF correction, not exact sequence importance sampling. A gate failure produces no optimizer step. Initial tensors/RNG, actual selected HF logps, twelve replay gates, total and negative-token component gradients, optimizer/RNG, adapter/state/binding and STEP_COMMIT are saved.

MAIN alone launches under the shared lock and an external 1200s timeout:

```sh
/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/openai-mrcr-cp32-fresh8-final-rloo-v1/owner.py run
```

Science cap900s; finite owner1100s. Output outputs/attempt-001; fixed checkpoint checkpoint-0001. No new native sampling, heldout queries or automatic resume. Saved full Adam/RNG supports an explicitly authorized later continuation, not an implicit restart. Primary future evidence is qualified fixed held/long rollout readout, not post-step likelihood.

Preparation uses the test-first/verification workflow: actual source authentication plus a real tiny HF/PEFT streamed-gradient fixture, injected replay mismatch/no optimizer, and actual train entry through full CPU preflight to its GPU guard. No sealed source or existing output is changed.
