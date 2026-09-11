# Complete-demonstration SFT — no terminal-supervision benefit, substantial matched regression

The full independent audit confirms unchanged low66c solves8/16, while action-only and action+terminal each solve1/16. Adding authentic terminal supervision changes neither correctness nor strict-format success on any paired coordinate. Both trained arms regress relative to unchanged. All48 endpoints are actual available native finals with verified physical branches; there are zero NULLs. This completes the audit and supersedes the preliminary endpoint-only publication.

| Root | Correct /16 | Strict format /16 | Correctness versus unchanged W/L/T | Last observation is scalar |
|---|---:|---:|---:|---:|
| Unchanged low66c |8|14|—|13/16|
| Action-only, fixed4 |1|12|1/8/7|1/16|
| Action+terminal, fixed4 |1|12|1/8/7|1/16|

Primary action+terminal−action-only is0 wins,0 losses,16 ties, net bounds[0,0], for both correctness and format. Each trained−unchanged correctness contrast has bounds[−7,−7]; format has2 wins,4 losses,10 ties, bounds[−2,−2]. Four decimal responses in each trained arm remain observed errors, without coercion. The trained arms share the same sole successful coordinate.

By helper partition, unchanged gets4/8 training and4/8 validation; each trained arm gets1/8 and0/8. By task, unchanged gets3/8 single-user and5/8 union; each trained arm gets1/8 and0/8. Context successes, in order new-root-train-00, train-01, validation-00, validation-01, are unchanged4/4,0/4,2/4,2/4 and each trained0/4,1/4,0/4,0/4. Exact pairs, context/partition/task tables and costs remain in PRELIMINARY.json and METRICS.json.

These are four context clusters with nested tasks/seeds, not48 independent source observations. The panel is disjoint from5852 excluded normalized groups across nine named catalogs, with32 helper-training and32 helper-validation groups independently reconstructed from source bytes. It is not globally fresh or pretraining-clean; licensing remains unresolved. Different training/serving phases are sequential. No significance, broad RLM gain or adaptive-planning claim is warranted.

## The extra loss was already nearly saturated

The complete arm's first weighted terminal objective is2.00172e−8, compared with action objective0.810361. Across its four updates, terminal contributions are2.00172e−8,3.24845e−8,8.75936e−8 and1.54747e−7, while action objectives fall0.810361→0.629360→0.484288→0.369843. Action-only falls0.810361→0.628528→0.482982→0.370958.

Thus the additional teacher-forced task—copying an already displayed scalar into `Answer: N`—has almost no remaining token prediction error under the starting root. This strongly limits what this particular terminal target can teach about choosing a reduction, query scope or handling a map. It does not measure gradient share, prove zero terminal gradient, or show that terminal supervision generally cannot help. The two final adapters are not identical: their actual L2 separation is0.0512362, versus distance from common start1.34735 action-only and1.34866 complete.

The scientific implementation matches its declared loss. All192 ledger terms across eight optimizer updates have independently checked coefficients, token counts, CE sums, weighted contributions and totals. Each arm has exactly four fresh AdamW steps over the same16-example order per update, lr1e−4, zero weight decay, default(.9,.999)/1e−8 Adam parameters. Each update has2472 action targets; complete additionally has84 terminal targets. Total action exposures are9888 tokens per arm, plus336 terminal tokens for complete. Complete has128 root-turn exposures versus64 action-only. Coefficient mass is1 versus1.1; compute is not matched.

All eight checkpoint chains, optimizer step counters1..4, finite moments, recorded RNG states,504 FP32 LoRA tensors, nonzero adapter changes, source-load equality and fixed checkpoint4 selection verify. The child is not loaded or updated by training. Actual served adapter/config files, descriptor and live-model crosswalks match the selected checkpoints. Training costs49.028s action-only and80.740s complete; no best-checkpoint substitution or extra optimizer pass occurred.

## The captured corpus is authentic, including its two wrong scalars

All16 original canonical authored actions are unchanged, in exact source order. Capture has80 native calls:32 authored root responses and48 actual c32 model child responses. Each example has two exact root prefixes, one actual scalar observation and a final native target equal to that observation. Every second prefix independently re-renders to physical native wire IDs; action and terminal target suffixes, EOS151645, full prefix masks and corpus hashes verify.

Fourteen captured scalars equal independently recomputed dataset counts. Two intentionally do not: train-02/global captures8 versus dataset9; train-06/global captures11 versus dataset10. The terminal targets remain8 and11. This is authentic execution supervision, not semantic-label correction or successful-trajectory selection. The all16 CORPUS_READY is SHAab32e50da46f0bdcd7369e1dc0ee7eb56b91221fac2339ed0df5d75b0a1288ff; neither training reads a different corpus.

The32 proxy root responses carry synthetic zero logprobs required by transport. They are explicitly authored, not sampled from low66c; a routed alias/hash does not make them behavior-policy samples. All48 child responses exactly match uniquely identified actual service proxy body/response pairs and native captures. The2556 authored root target tokens are separate from7054 actually sampled child tokens. No authored likelihood, dummy host verifier reward or admission enters an RL export. All prior system/user/action/child/observation positions are masked from the current root target.

## The observed bottleneck is scope and reduction, not final scalar copying

Both trained arms end15/16 episodes after displaying maps, versus3/16 unchanged. Their complete source-bound child unions cover the requested scope in16/16, and literal root-visible map unions cover it in15/16. In12/16 trained episodes, those supplied labels imply the correct scoped count but the actual final answer is wrong. The root has usable labels yet does not carry out the required scoped reduction. Coverage alone is not proof of consumption.

For a concrete matched example, new-root-train-00/union seed981330202 has gold1. The complete root runs four four-record classification calls, printing all16 labels in four tool observations. Its visible map union gives1 for u00/u01 but4 across all users. It returns `Answer: 4` without executing a scoped count. The unchanged root initially makes a wrong metadata-key lookup, inspects a record after the resulting KeyError, then filters on `record["user"]`, computes and displays1, and returns `Answer: 1`. This illustrates retained adaptive recovery in the control and a concrete scope omission in the trained rollout; it is a selected mechanism example, not a causal prevalence estimate.

The complete example raw episode SHA is e5f555f967fcfc2f5f2622cf56fc566965d78a5927e5c358f80676392dd6a185; matched unchanged SHA594abd6a23b4b3212d6139c418e51d0b6197195cd07e4f0ace0f595ec030d217. Full raw paths, verbatim captured code and observations are in READOUT_AUDIT.json. No generated code was executed during this audit.

The sole trained success uses one16-record child request and an unfiltered count of human-being labels; it happens to equal the scoped gold1. Endpoint correctness is retained, but this does not demonstrate learned filtering. Across all arms, every correct last displayed scalar is finalized correctly: eight unchanged, one per trained arm, zero correct-last-scalar/wrong-final cases. The current terminal targets therefore address an already strong copying boundary while sampled rollouts rarely arrive at that boundary correctly.

## Native traces, child semantics and costs

All459 capture/readout physical attempts return; all role/typed request/result IDs reconcile, with no request-only/provider-failed attempts. All459 native graph prefixes and physical token/logprob records verify. All202 child requests independently match exact public text/ID order and ordered grammar, and all202 semantic child→root call edges verify separately from physical ancestry. No root grammar is imposed.

Readout calls are unchanged103=71 root+32 child, and each trained138=77 root+61 child. All154 readout child maps are valid. Dataset label agreement is185/192 unchanged,244/256 action-only and245/256 complete, with target FP/FN0/5,0/6,0/6 respectively. Counts are label occurrences, not independent semantic adjudication. Both trained arms use60 width4 calls and one width16 call; unchanged uses22 width4, seven width8 and three width16. All177 captured readout root cells parse as Python; static parsing is not program execution or proof of consumption.

| Readout root | Logical input | Output / sampled action tokens | Cached input | Uncached input |
|---|---:|---:|---:|---:|
| Unchanged |138852|11973|130688|8164|
| Action-only |159312|8515|152416|6896|
| Complete |159318|8511|152416|6902|

All readout usage fields are known. Capture actual c32 usage is54728 input,7054 output,45104 cached and9624 uncached. All four usage fields are unknown for the32 synthetic root responses and remain unknown; their known authored target-token lengths are not fabricated billed usage. Grouped context/helper-partition/task cost tables are in METRICS.json. Lower output totals with sharply worse accuracy are not evidence of useful efficiency.

Capture elapsed328.429s. Readout elapsed144.536s action-only,149.815s unchanged and147.392s complete. Scientific total1094.869s and parent1095.558s include startup, orchestration and release; the difference from summed collection/training times is not assigned to model work. Parent EXIT is0, not timed out, with empty post-exit GPU PID inventory. All four owned service releases verify exited identities and free ports. Shared caps remained capture1080/training480 each/readout420 each/work3450/cleanup120/owned3570/outer3600 seconds. The original attempt's4.943s failed setup and48 unrun NULL slots remain a separate preserved operational failure, not extra scored trials; recovery used a fresh corpus/optimizer and the accepted unchanged scientific inputs.

## Ranked follow-ups and disposition

1. Prioritize query-scoped map→executable-reduction supervision on disjoint training compositions, with actual native map/error prefixes and a meaningful remaining prediction error. Compare a small matched corrective-action treatment against unchanged root, retaining strict endpoints and observed scalar boundaries. Promote only if it improves held-out scoped correctness and actually restores reduction/filter behavior; reject a mere format gain or another copied-scalar ceiling.
2. Calibrate the mechanism with separate supplied-correct-map and actual-child conditions on fresh8/16/32-record count/checksum tasks, stratified by scope. If supplied maps still fail, root scope/container/reduction is the limiting link; if they pass while sampled children fail, pursue child semantics/width. This complements the independently queued reducer diagnostic and does not authorize relabeling these results.
3. Retire this exact16-example, four-update recipe as an improvement candidate. Do not add epochs solely because training action CE decreased. Before any new training, require a prospective target that addresses the observed rollout failure and an unchanged-root control.

Completed: source/selection audit,16-example authentic capture, all masks/targets, eight optimizer checkpoints,48 independent endpoints,459-call native/usage audit,202 exact child contracts/semantic edges, scoped visibility mechanisms and release provenance. No audit stage remains pending. New experiments and confirmatory replication remain future work. No GPU/service/source/queue mutation, model load or generated-code execution occurred.

Artifacts are in `analyses/root-complete-demonstration-sft-live-2026-09-09`: METHOD_READY and PREPARATION_READY preserve the outcome-blind boundary; OUTCOME_PINS freezes actual runtime JSON; PRELIMINARY retains its original partial label; CAPTURE_AUDIT, TRAINING_AUDIT, READOUT_AUDIT and METRICS provide full evidence. FINAL_MANIFEST seals those files, scripts and this report. Scientific terminal SHA7b88de130b514b0e0e72494fce4db7f89792fd7a27ef5fd3b8fc8f33e540cb1a. All historical preparation and prior-study seals remain unchanged.
