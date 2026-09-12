---
question: Does smaller public scope reduce omission or invalid eligible-ID claims at fixed total output budget?
mode: exploratory_fixed_fanout_not_learned_depth
cases: 9
widths: [6, 12, 20]
helpers: [1, 2, 4]
repeats: 2
physical_calls: 126
stage_policy_outputs: 54
science_seconds: 600
owner_seconds: 700
external_seconds: 800
workers: 4
launch_authority: MAIN_only
---

Nine outcome-blind new stages (three per width), disjoint IDs from the original eight roots. Every candidate keeps its complete original implementation/change/check history; policies and domain remain unchanged. Partitions are hash-ranked candidate IDs, never eligibility-ranked. Each model sees only its assigned public shard and the same reviewed IDs-only instruction. Host gold is0600 and used only in metrics. No host eligibility repair: take the union of exactly claimed IDs after strict scope/JSON validation. No root synthesis/model call.

Released Qwen3-4B-Instruct-2507, no research adapter, same native renderer/T.5, top_p1, top_k−1, min_p0, cache_salt0. Fixed seed `202609310000 +100*case_index +10*repeat +part`; first-part seeds paired across k, additional parts have fixed offsets. k order rotates by `(case_index+repeat)%3`; cases run on four workers, each case's14 calls serial. Physical interleaving may vary; per-condition requests and seeds do not. No retries or early model-score stopping.

Output caps are384/192/96 per helper, total384 per stage-policy. All-assigned-ID canonical compact JSON plus EOS fits every shard: maxima269/140/74 tokens for k1/2/4, with actual full input+cap≤6297 across the frozen inventory. This proves the required concise payload can fit, not that arbitrary explanatory text will fit. Splitting duplicates policy/prompt input (n6 approx2.1k→3.8k total input; n20 approx5.9k→7.6k). Count length stops, output tokens, physical calls, observed usage subtotals and unknown-usage calls; no matched total-input-cost claim.

Primary: eligible-ID exact sets for all18 planned stage/repeat observations per k, with available/invalid/unavailable counts explicit. TP/FP/FN and precision/recall use strictly valid sets. Paired exact wins/losses among available outputs count invalid claims as known failures; strict-valid-only pairs are also retained. Do not turn transport unknowns into empty sets or wrong answers. Repeated decodes are not independent cases: n=9 case units, only3/width. No hypothesis test or best-k confirmation. Every k/repeat stays scheduled regardless prior answers. Completeness depends on runtime/raw availability, not correctness.

Decision: a favorable scope/cost pattern may justify a new held-out fixed-versus-adaptive fan-out study; this run cannot establish learned delegation/depth or recombination skill. If extra helpers only add cost or invalid output, retire this budgeted partition configuration rather than increase caps post hoc. The stock generator has planted feasible candidates and remains a candidate benchmark, not a general database distribution. Prior IDs-only24 readout was mixed (more exact sets but more invalid claims); this new comparison is not preregistered independent confirmation of a broad gain.

Raw starts, exact request bytes, response bytes, prompt/token/schema/finish/usage receipts are saved per call. Partial/error/start-only inventory remains inspectable. Reuses reviewed V3 ownership/actual first-dispatch kernel qualification at final release, not a startup log-line proxy. GPU and private credential are required only for MAIN's actual owner run; CPU guard rejects before creating attempt output.

CPU: `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python owner.py verify`

MAIN launch argv is in READY_RUN.json: native Python, owner.py run --outer-seconds700. MAIN must supply the shared GPU flock and800-second external timeout; no subagent launch. Output is outputs/attempt-001, never resumed/overwritten. Frozen feasibility manifest retains its original single-repeat63-call feasibility count; this additive run prospectively doubles repeats to126 without rewriting it.
