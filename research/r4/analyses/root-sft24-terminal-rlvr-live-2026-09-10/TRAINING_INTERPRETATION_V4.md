# Warm V3: closed training, before final-outcome access

All192 original rollout slots were actually attempted and exported.184 have native endpoints and are training-admitted;8 remain NULL.125 admitted terminal successes are **training outcomes**, not a matched improvement estimate. Eleven mixed prompt groups supplied84 selected episodes to seven real optimizer commits. Optimizer time alone totals219.2304703 seconds; acquisition, startup/release, CPU replay, model load and checkpoints are additional costs. No final-readout content has been opened.

| Window | Planned/attempted/exported | Available/admitted | Positive | Mixed prompt groups | Selected episodes | Commit |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
|1, original capture reused|24|20|18|2|13|1|
|2|24|23|10|2|15|2|
|3|24|23|9|1|8|3|
|4|24|23|21|2|16|4|
|5|24|24|9|1|8|5|
|6|24|24|14|1|8|6|
|7|24|23|20|2|16|7|
|8|24|24|24|0|0|noop|

Each window has three identical-prompt groups of eight sampled rollouts. Window8's count-single(gold0), distinct-union(gold1), and weight-union(gold3) groups are each8 successes,0 failures,0 exclusions. Their normalized advantages have no variation; the exporter records training_group_episodes0 and no GROUP.json is written. The owner truthfully consumes window8 without training, retains exact checkpoint7, and reports completed_windows8/optimizer_steps7. This is not inaccessible reward or a failed trainer. Conversely, windows3/5/6 each have an all-failure weight group that contributes no gradient. `TRAINING_INVENTORY_V4.json` contains all24 per-prompt admitted0/1/excluded counts, not only these examples.

The task/context changes between windows. These numbers are **not a learning curve** on a fixed task distribution, and there is no contemporaneous unchanged-policy training comparator. All training queries are the existing count/distinct-user/weight primitives, not the three composed operators of the final panel. Seven commits do not establish composition transfer.

## Fixed positive-program sample

The post-training sampling rule was written before reading sampled code: lowest coordinate ID per endpoint-positive prompt group, plus an excluded zero-gold positive if needed. It selected21 trajectories from21 positive groups, including three zero-gold groups; there were no positive-but-training-excluded extras. This deliberately positive sample cannot estimate the faithful rate among all125 positives or all192 attempts.

Actual native tokens/messages, weight aliases, graph ancestry and final branches were authenticated for all21. Manual review of every selected program and observation found **19 faithful requested primitive computations and two wrong-scope coincidences**. All21 acquire actual c32 predictions and use the live returned map; none merely guesses a scalar or reconstructs a label dictionary as a literal. There are24 child calls:20 examples use one full16-record call, and one uses four4-record calls. Sixteen examples' acquired maps contain at least one semantic label error; a correct scalar is not a perfect map.

- The real multi-call example is `training-02:distinct-union` (sample7): four observed map sizes4→8→12→16, `record_map.update` after each actual child return, then the requested union-user/location cardinality prints2 and native `Answer: 2`. This is genuine retention plus requested primitive reduction on a training task, not evidence of scale generalization or composed reasoning.
- Samples10 (`training-03:weight-all`) and15 (`training-06:count-all`) wrongly restrict the supposed all-record scope to u0/u1/u2, omitting actualu3. Both still receive reward because no omitted user record qualifies in the observed maps; their printed5 and1 match gold. Terminal reward therefore does not exclude all scope bugs.
- Zero-gold samples9,16,18 acquire the real map and execute the requested scoped set/count operations before printing0. They are constant-compatible outputs but **not constant-output programs**.
- Samples0 and2 recover from real execution errors: session-directory serialization in0; twice indexing child.answer as a dictionary in2, then using json.loads and the requested weight sum. Successful continuation is observed, not inferred from a final string.
- Five faithful examples have changed target-membership labels inside the requested scope despite a correct scalar (samples3,4,5,11,14). Counts/weighted sums can cancel label errors; distinct-user counts can be unchanged by mistaken record membership. Retain the child-semantic versus operation distinction.

All three sampled window1 positives—before any new RL update—already implement the requested primitive correctly. Thus the sample establishes accessible on-training behavior and actual rewarded actions, **not that RL newly learned those behaviors**. All selected observations come from the exposed original SFT/QSR training contexts. No protected-context or final efficacy claim is made.

## Artifacts and implications

- `TRAINING_SAMPLE_METHOD_V4.md`:post-training, aggregate-aware sample rule.
- `TRAINING_INVENTORY_V4.json`, SHA `45fd269f3d18b4856269e973068880c932eb8bced1acfb490742a2300ba4915d`:192-slot reconciliation, all24 prompt counts and pre-code sample selection.
- `TRAINING_SAMPLE_EVIDENCE_V4.json`, SHA `0bf73f8219f3e57e14cf2381a81db14dcaa4997cc301484686fa786268756877`:21 exact paths, native verification, complete programs/observations, actual child maps, semantic errors and manual classifications. No sampled code was reexecuted; host reductions are separate diagnostics over parsed returned data.
- `CHECKPOINT_CHAIN_V4.json` and `CLOSED_TRAINING_WIRE_V4.json`:saved-payload and physical accounting from the prior staged seal;1047 training calls, not zero or merely routed-audit file counts.

runtime_port authored V3 recovery and these analyses; overlap is explicit. MAIN retains independent decision authority. Nothing here changes live checkpoints, rewards, final inputs or queue. Await the matched96 final endpoints: only those can distinguish primitive retention, new composed execution, missingness and scope-coincidence changes under the fixed last policy. The parameter-sensitive SFT design remains conditional; this training sample is neither a reason to launch it automatically nor to declare terminal RL successful.
