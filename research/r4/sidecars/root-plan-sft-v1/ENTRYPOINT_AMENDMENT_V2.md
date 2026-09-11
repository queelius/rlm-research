# Additive prelaunch entrypoint correction

MAIN authorized this correction after independent storage review reproduced a real import failure in the sealed readout.py. Original READY6c511ac8…, sources, prepared-v2 corpus, RECIPE_V2/INPUTS_V2, qualification001failure and qualification002PASS remain byte-unchanged. No model/training/readout has started for this study.

The pinned inherited readout contains **two** literal `prepared/PLAN.json` references: the plan load and READOUT_BINDING plan hash. Original study.private erroneously asserted one. The composer-only smoke test did not import this outer readout and therefore missed the defect. ENTRYPOINT_FAILURE_V1.json preserves the actual original `readout.py --help` failure and traceback, GPU0.

readout_v2.py is a flat explicit copy of the pinned inherited collect/CLI, not another wrapper around the broken module. Both PLAN paths and the one PROMPTS path explicitly point to prepared-v2; the CLI lists unchanged/canonical/filter_first. It keeps the same current study/binding modules and existing counted inner16-coordinate adapter. A cached verify_corrected authenticates original READY, additive READY_V2, exact unchanged scientific input map and new source closure; it returns the **original scientific identity** used by unchanged train.py/binding.py. AST tests show collect differs only by the three file paths and readiness authentication call.

launch_v2.py is a flat explicit copy of sealed launch.py: it imports the actual corrected readout, authenticates READY_V2 before any work, invokes readout_v2.py for each phase, and records READY_V2's hash in RUN. Its scientific identity, two train.py argv, original output path, phase order,48 denominator, callbacks, caps and release behavior are unchanged. An AST test compares the exact execute body after these three operational substitutions; a fake-external-boundary test executes this corrected body through two training and three readout stages. No changed task, target, seed, LR1e-4, root66cce start, childc32, checkpoint selection, native runtime or grammar.

Regression sequence: three new tests observed RED before additive files existed, then GREEN for actual readout_v2/launch_v2 --help imports and flat-body comparisons; the actual original failure is separately reproduced and preserved. A fourth check executes corrected48 workflow with fake processes/services. These are CPU tests, not actual model calls or a repeated runtime fixture. Existing8 tests and7-call native qualification remain relevant and unchanged; rerun tests are saved separately as CPU_TESTS_V2.json.

Corrected acceptance target is READY_V2.json only. Its argv is:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-plan-sft-v1/launch_v2.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-plan-sft-v1/outputs/attempt-001
```

Verification: same Python and launch_v2.py with `verify`. Caps remain2430outer/2400owned/2280work,2×360training and3×420collection clipped to shared remaining time. Do not invoke original launch.py, whose original readout path is intentionally preserved as failed prelaunch evidence. MAIN alone accepts/launches; no implicit fallback between versions.
