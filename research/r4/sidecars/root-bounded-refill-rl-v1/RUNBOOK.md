# Bounded refill RL — parent-only launch

Question: does prospective bounded extra sampling obtain within-prompt reward support from a fixed complete-success-SFT8 warm start, and what happens to the last committed policy? This is not a randomized refill/no-refill treatment comparison.

Run with the existing qualified native interpreter:

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-bounded-refill-rl-v1/coordinator.py verify
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-bounded-refill-rl-v1/coordinator.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-bounded-refill-rl-v1/outputs/attempt-001
```

MAIN must authenticate READY/source closure, supply the exclusively owned single CUDA device and existing service credentials, and hold the shared operation lock after the exact predecessor and empty-GPU checks. No service may overlap. External command envelope3630s; owned3600s includes120s cleanup, shared work3480s. No automatic resume, rerolls, checkpoint substitution or timer reset. A stopped attempt is preserved; any continuation requires a new additive MAIN decision and namespace.

Baseline/final24 use exactly the same new seeds and prompts. Each collection uses four slots, .5/full-support native root sampling, unconstrained root actions and fixedc32 request-local typed child. Groups are serial eight-slot batches so support can decide the next frozen group. The actual qualified single service may stay warm across homogeneous no-ops; updates release it and restore the exact new policy. Existing exact PID/start/UID/PGID/config and descendant-release lifecycle is reused unchanged.

Output layout: RUN.json; services/*; readout-before and readout-after/{rollout,export}; window-01..04/GENERATION.json; group-1..4/{rollout,export}; union/{EPISODES,GROUP-if-mixed,MANIFEST}.json; training/checkpoint-{actual-step}/{adapter,optimizer,RNG,state}; WINDOW_RESULT.json; SELECTION.json and FINAL.json, or immutable STOP-*.json. Candidate-window numbers and actual optimizer-step numbers deliberately differ after a no-op. Checkpoint state is the commit; there is no fake no-op checkpoint.

An incomplete/capped/integrity-failed sampled window never updates. If cutoff is reached between completed windows, select the last real policy0–4 and run final readout using its660s reserve. A stage failure stops the run and leaves later cells unrun/NULL. Completed wrong/empty/malformed endpoints are binary0 only when the unchanged native graph admission passes. Provider/setup/finalize failures remain NULL. Excluded calls still cost compute; selected success does not verify a faithful plan.

CPU evidence: test-first prefix/dispatch regressions; actual inherited mixed selector and native three-call fixture reconstruction; exact root/child grammar and mask checks; actual tiny-CPU TIS/Adam checkpoint updates on both sides of a true no-op; unchanged optimizer/RNG through no-op; stale and double-step rejection. Synthetic qualification likelihoods are rejected by the scientific exporter. The GPU model and scientific run are not exercised during preparation.
