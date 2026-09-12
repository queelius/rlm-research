# Fixed-dose readout analyzer

This is a one-shot CPU analyzer, not a monitor or experiment owner. It never executes generated
code, submits prompts, alters a training/gating decision, or selects an intermediate checkpoint.
Invoke after the accepted evaluation operation terminates, or deliberately create a named pending
snapshot. A stage is read only after both its scientific RESULT and OWNER_TERMINAL exist.

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/analyses/openai-mrcr-procedural-sft-dose32-readout-2026-09-12/analyze.py verify
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/analyses/openai-mrcr-procedural-sft-dose32-readout-2026-09-12/analyze.py run --output /project/alex_phd/runs/rlm-research-r4/analyses/openai-mrcr-procedural-sft-dose32-readout-2026-09-12/completed-readout-001
```

Use a new direct child output directory each time; existing reports cannot be overwritten.
The JSON report records each consumed source hash. CPU_READY seals fixed analyzer and evaluator
provenance; future evaluation outputs are captured by hashes at the terminal snapshot, not guessed.
The script prints pending explicitly if outputs are absent and never waits or retries.

Read clean correct-target observations followed by a wrong final separately from clean wrong-record
prints, broad dumps, actual Python schema errors, and first-action teacher AST matches. AST patterns
are candidate diagnostics, not a proof that arbitrary programs are correct. Lower pre-update
teacher loss alone does not demonstrate procedure acquisition. Raw final strings are never repaired
for the primary metric. Held base/final32 has16 contexts with two repeats; train checkpoint4/final32
pairing requires matching coordinates, seeds and available physical initial-prefix evidence.

The focused tests reuse actual archived checkpoint4 outputs. No broad suite or GPU is required.
