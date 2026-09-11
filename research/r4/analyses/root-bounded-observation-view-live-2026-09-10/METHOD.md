---
schema: bounded-observation-view-audit-method-v1
status: prospective_before_launch
frozen_utc: 2026-09-10T10:22:35.085401560Z
scientific_attempt: sidecars/root-bounded-observation-view-v1/outputs/attempt-002
ready_sha256: 889b59bef1acb1e0e14d2e494182cee5b599fa40486bda816b5128893038530f
author_overlap: question_cards authored bounded V1 and additive V2; did not author accumulation parent or its mechanism audit
outcomes_read_before_freeze: none; attempt-002 did not exist at freeze
---

# Prospective audit: bounded passive observation view

## Estimand and limitation

The fixed 32-row experiment crosses BATCH versus CUMULATIVE decoder returns with the existing 20,000-byte native tool-output view versus a 4,096-byte head/tail payload view. The causal contrast is the passive tool message presented in subsequent root requests. The 4,096 number is retained raw payload bytes; warning and omission-marker text are additional visible bytes. It is not a total-message-token limit.

V2 creates no task-working-directory raw ledger. It retains the complete tool result in nano-RLM's pre-existing session log, adds only view hashes/sizes there, and harvests those entries after rollout. The system prompt advertises the conversation-log path. Therefore this does not enforce information hiding: a policy can deliberately read the full log. Any such read is reported, and the estimand remains passive observation presentation rather than filesystem access control. V1 was never launched.

## Inventory and evidence admission

Audit every one of the 32 frozen coordinates and preserve its planned cell, block, source context, seed, operator, size and gold. A native final is available only when the frozen collector's authenticated final branch and native token/body evidence agree. A completed authentic wrong or malformed final is zero. Missing result, unfinished tool branch, inconsistent wire evidence, provider failure and unstarted slots are NULL, separately typed. OWNER completion never implies endpoint availability.

For every coordinate, inventory `RESULT`, `EPISODE`, `FAILURE`, role/typed audit, physical requests/responses and harvested session entries when obtainable. Do not repair answers, execute sampled code, reconstruct a final from prose, substitute another cell, or discard a malformed completion. Recompute `Answer: N` and host gold independently from frozen public records/private labels and the requested operator/scope.

## Intervention integrity and exposure

Verify before interpreting scores:

1. Model, adapter, role aliases, source files, query, seed, sampling, 2,048 action cap and 8,192 context cap match READY and are paired within block.
2. Each U-shaped control here is actually the 20,000-byte view and each treatment is 4,096; both contain the same neutral session metadata schema. No task-visible raw ledger exists.
3. For each IPython tool result, match the existing raw `tool_result` to the adjacent view record by session/turn and raw hash. Recompute raw bytes, head/tail payload, marker text, visible hash and marker overhead.
4. Count clipped tool results that occur before a later root request. Decode that later native request and verify it contains the recorded visible view. Report whether excluded middle content is absent. Merely clipping after the final request is not an exposure.
5. Search actual sampled root code and filesystem actions for reads of `RLM_SESSION_DIR`, `messages.jsonl`, `.observation_view.json`, session directories or other raw-log/config paths. Report actual reads separately from string mentions. Inspect child sessions for tool calls and clipping; do not assume children never use tools.
6. Attribute every HTTP 400/context rejection to root or child from the authenticated alias/body. Report actual prompt-token IDs/usage or their absence; do not infer context overflow from status alone unless the retained error evidence supports it.

## Behavioral mechanism audit

On all available finals, inspect actual code, child requests/finals, IPython observations and retained state without reexecution. Record:

- genuine child acquisition and exact-ID decoder admission;
- number and sizes of distinct acquired batches;
- whether two or more batch maps coexist in live variables rather than only in printed literals;
- whether the final computation uses the requested operator, scope, target category and public weights;
- whether observed child-label errors alone explain a faithful wrong answer;
- whether stopping follows the computation without an outstanding tool call.

Classify each available endpoint as `faithful_correct`, `faithful_wrong_child_error`, `faithful_wrong_other`, `wrong_operator_or_scope_coincidence`, `literal_result_without_supported_execution`, or `unsupported_manual`. Literal reduction is task behavior but distinct from retained-state reduction. Scalar agreement alone is never mechanism proof.

## Planned summaries

Primary tables use all eight paired blocks and all 32 planned endpoints:

- strict correct / planned, native available / planned, and NULL bounds by decoder-return arm × view;
- within-block 4,096-minus-20,000 differences for BATCH and CUMULATIVE separately;
- clipping, exposed-before-next-root clipping, deliberate session-log/config access, root/child HTTP400, acquisition, retained multi-batch state, faithful reduction and stop;
- parent-context and 128/256-record strata, explicitly clustered rather than record-independent;
- all-available semantic taxonomy, alongside conservative planned denominators.

Report paired wins/losses/ties only when both endpoints are available; also report discordant availability and conservative bounds so pairing does not select successful responses. The decision signal is improved availability plus at least one genuine retained-state multi-batch reduction in the 4,096 CUMULATIVE arm. Availability alone supports an interface fix, not accumulation competence. Failure to improve is informative only for this payload/view and exposed panel.

## Physical cost and closure

Union planned directories, `RESULT`, `FAILURE`, role/typed audit and every physical request/response artifact. Separate prepared/unstarted, response-proven attempts, HTTP errors, choice-bearing completions, authenticated native finals and unknown usage fields. Sum known prompt/completion/cached tokens by role and cell; retain unknown counts. Do not call local compute provider billing. Reconcile owner/start/service/release/parent clocks against 1,800 outer, 1,770 owned, 1,650 work, 180 startup, 1,440 collection, 120 release and 30 harvest. Seal the eventual report, tables, annotations, source pins and all output hashes without modifying scientific artifacts.
