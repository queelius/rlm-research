# Short32 additive V2 review guide

This is a review map for the additive repair only. V1 remains preserved and is imported rather
than copied. `CPU_READY_CONDITIONAL_V2.json` is conditional CPU evidence, not GPU launch authority;
`READY_V2.json` must not exist until the actual V7 prerequisite passes.

## Recommended reading order

1. `REVIEW_AMENDMENT_V2.json` — scientific boundary: strict model-stop allowlist, exact causal
   mapping requirement, raw-native runtime evidence, and the non-enforced read-only instruction.
2. `classify_v2.py` — only authenticated `agent_completed` terminals and the four named model
   budget stops can become observed model outcomes. Trace/native ambiguity remains unavailable.
3. `causal_map_v2.py` — reconstructs each sampled call's complete causal prompt and trailing action
   span from its physical parent chain, then requires a one-to-one native-audit match on prompt IDs,
   completion IDs, logprobs, digest, model, sampling and finish reason. Root versus child is derived
   from `subagent_call` ancestry on the physical branch. It does not confuse child invocations with
   child turns or falsely equate ACP request IDs with provider response IDs.
4. `collect_v2.py` — the small overlay that replaces V1's classifier and trace inspector in memory;
   task selection, prompts, G4 schedule, scoring, concurrency and service request path remain V1.
5. `owner_v2.py` — additive `attempt-002`; V7 qualification reads raw result files and requires
   `status=returned`, with zero errors, other statuses, orphan starts/results, and PendingTurn
   serialization errors. It has no fallback to aggregate result-file counts.
6. `finalize_after_v7_v2.py` — write-once conversion from conditional receipt to `READY_V2.json`.
   Its <=600-second evidence is explicitly the whole-owner elapsed time, a conservative upper bound
   rather than a measured science-only interval.
7. `test_short32_v2.py` and `CPU_CHILD_ROLE_SMOKE_V2.json` — focused regressions plus an actual
   runtime/renderer/recorder fake-provider episode with roles root, child, child, root. This proves
   two child turns are not one child turn merely because there was one recursive invocation.
8. `prepare_v2.py` and `CPU_READY_CONDITIONAL_V2.json` — closure, dependency, fixed argv, attempt,
   caps and frozen-input pins.

## Unchanged science

- First eight frozen `DATA_READY_V2` training contexts, four rollouts each; no heldout model query.
- Same original JSON context bytes, questions, seeds, Qwen3-4B no-adapter root/child, temperature
  0.5, 2048 tokens/call, depth one, six completed root-plus-child turns, official OpenAI scorer.
- No optimizer, retry, confidence signal, solver hint, post-outcome selection, or changed gate.

## Evidence and boundaries

- Conditional receipt SHA-256:
  `fab9c2581a33fe039c3adff3abc3982188cc3a995bc300bccfa39f4ed46061da`.
- Conditional identity:
  `106b260675dbf483c20559af7734d33be3a9ea4b0cc2fa3c71097846cf19d304`.
- Forty-four closure hashes were current at sealing; seven focused tests passed.
- The child-role smoke used a synthetic CPU provider and synthetic logprobs but the actual renderer,
  RLM harness, Docker task environment, V7 recorder and four-turn graph. It is protocol evidence,
  not model-quality evidence.
- Exact duplicate prompt/action/logprob tuples would make matching non-unique and therefore
  unavailable; the mapper does not choose one silently.
- The local context source is mode 0444 and its initial bytes are verified. Runtime filesystem
  immutability against model-generated code is not enforced.
- Calibration delegation summaries remain observational. Root-only RL additionally requires every
  selected trajectory to pass the exact causal mapping; counts or session IDs alone are insufficient.
