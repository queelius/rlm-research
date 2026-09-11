# Root-only learning with a fixed trained child

Decision2026-09-08 22:16 UTC. This is an adaptive exploratory followup, prepared
while the current role-isolated evaluations use the A100. No approval pause is
needed under the user's research instructions. Work additively outside sourceGit.

Motivation: supervised child accuracy improved strongly, but root code still fails
to call tools, parse returned JSON, cover records, or aggregate correctly. Earlier
terminal-reward all-action RLVR also rewarded misleading child/process behavior.
Do not alter historical rewards. Test a different intervention on fresh data:
update only root actions while keeping the selected child adapter fixed.

Phase1: collect actual native TrainClient root/child trajectories under original
root and the validation-selected leaf SFT checkpoint. Both roles use the native
Qwen3 nonthinking template (renderer enable_thinking=True removes the generic empty
thinking prefill; it does not activate thinking). Keep temperature0.5 and full
top-p/top-k/min-p support for both roles,2048token call cap, depth1/no compaction,
unchanged public definitions-enabled executable example, unchanged strict final
count reward. No grammar/constraints, output repair, or answer fallbacks.

Source design: load the5065 normalized officialTREC training groups from the frozen
trec-leaf-sft-v1 source helper, not its model outputs. Hash-sort using namespace
root-only-credit-v1 and seed981260400; take384groups, partition six64-record contexts.
Firstfour contexts are root-training (eight fixed HUM/NUM count queries); finaltwo
are root-validation (four queries). They are all disjoint from leaf validation/test
groups and from the384 new-composition evaluation groups. The child previously
trained on these questions; this is intended competence support, not unseen-leaf
evaluation. Synthetic Date/User fields remain independent of labels. Gold host only.

Collect32training episodes:8tasks×4freshseeds, all with trained child; plus8validation
episodes:4tasks×2freshseeds. Preserve per-episode outputs, model-call audits, actual
role aliases/depth/request IDs, native token IDs/masks and sampled logprobs. Existing
child-role EvalClient implementation is a reference, not itself a native capture
qualification. Additive native request-local routing must modify actual request model
after overrides without changing messages, sampler or shared context. Preserve the
rootless runtime and real-process CPU root→child→root qualification. Check actual
processed-logprob service setting, not a stale endpoint descriptor.

Root-only credit: reconstruct every call's true causal prefix from official physical
trace branches. Validate all call/node/role/alias identities, sampling and raw capture.
Export depth0 current actions only; their prior root actions and child/tool outputs
are masked context. Depth1 actions are retained as evidence but never credited or
updated. Do not retokenize message text to invent native IDs/probabilities and do not
falsify call models to pass the old all-policy exporter. Keep all policy outcomes;
incomplete/unobservable/transport failures are exclusions, not manufactured negatives.

An eligible nonempty correct native root action sequence can be trained regardless
of whether it recursed. Completed wrong/malformed final answers have reward0.
Use only within-task groups with actual mixed binary rewards for the first update.
Keep uninformative and failed groups in the audit. If no mixed group exists, stop
that learning attempt and propose a task/prompt intervention instead of endless seeds.

Phase2 (separately sealed once valid data exists): one root-only full-batch token-TIS
LoRA update, same exact original FP32 rank8 adapter, BF16 frozen base, dropout off,
AdamW LR5e-5, weightdecay0, gradclip1, cap2 conditional token correction. Use existing
distributional guards from single-gpu-rlvr-v2/TIS_V3_SPEC.json, not the abandoned
single-token max-drift gate. One step means HF old=current.detach is meaningful;
do not reuse that shortcut for multiple optimizer updates. Store all recomputed
probabilities, clipped fractions/ESS, gradient norms, parameter deltas, optimizer,
RNG and input identities. No claim of exact trajectory on-policy correction.

Primary immediate comparison: paired before/after root-validation8 with leaf fixed.
The already-frozen new-composition48 is later report-only transfer evaluation, not
an LR/threshold selection set. Run at mostone update before reassessment. Additional
rounds require fresh current-policy rollouts and a new iteration record, not repeated
training on stale probabilities. If useful signal survives process inspection, extend
to several fresh-policy rounds and then unseen layouts or source families.

Compute:40episodes,4concurrentworkers,1800second collection cap, atomic after each
episode, one-A100 inference then training sequentially. Optimization cap600seconds,
checkpoint immediately after any update. Phase1 CPU preparation must not start or
stop a GPU server. Parent controls device ownership and actual service binding.
