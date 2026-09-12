---
question: Does the LR1e-4 dose yield stronger local copying fit and/or exposed held transfer versus LR1e-5?
endpoint: original cp32 plus exactly one fresh8 RLOO LR1e-4 step; fixed checkpoint-0001
phases: [training32, exposed_short_held32]
training_seeds: 202609250000..202609250031
held_seeds: 202609270000..202609270031
per_phase_caps_seconds: {science: 900, owner: 1100, external: 1200}
new_optimizer_steps: 0
---

All32 original fresh8 training samples and all32 exposed short-held samples are fixed before new readout. Run BOTH phases regardless train score; there is no outcome gate between them. Reuse the qualified cp32 and LR1e-5 controls on their exact respective seeds: training7/17 correct, held25/25 correct, all32 available each. No baseline resampling, new long/four-needle panel, outcome-based selection or checkpoint search.

Keep original serialized context, prompts, Python harness, native renderer/parser/EOS, terminal-strip-disabled hooks, temperature.5,2048tokens/action,6total root actions,zerochildren,4workers. Model root alias is the LR1e-4 checkpoint; unchanged base/helper map remains bound but children are disabled. Full raw per-call/episode inventory and known error/stop branches are inherited unchanged.

The additive checkpoint qualifier retains all actual source, initial tensor,12HF replay/20skip, gradient/Adam/RNG, state/commit/result and service-weight checks. Only expected LR literals change1e-5→1e-4; replay/moment tolerances remain unchanged. Test actually qualifies the completed new endpoint and rejects old LR metadata. No new accuracy qualification is added.

Metrics: fixed C/W/U, paired wins/losses vs both cp32 and LR1e-5,8training G4 context units and16held paired-repeat units, copying versus clean-target/tool selection taxonomy, all changed native paths and physical/policy costs. Training fit is not transfer. Held contexts are research-exposed; any gain is exploratory development evidence, not fresh-test confirmation. These arms isolate nominal learning rate on the same frozen batch, but runtime arithmetic/BF16 casting can perturb the served dose.

The inherited train RESULT includes a legacy manipulation_gate field: explicitly inapplicable, never consulted by this owner or the held phase. A partial/failed train runtime does not score unavailable cases wrong or justify withholding held; MAIN retains both fixed phases under their independent caps unless service safety prevents execution.

MAIN only, separate shared exclusive GPU lock/external1200cap per phase:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py run --phase train
/project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py run --phase held
```

Outputs `outputs/train-001` and `outputs/held-001`. CPU verify replaces run with verify. Accepted service lifecycle authenticates binding and cleans up owned processes. No model calls or source changes occur during preparation.
