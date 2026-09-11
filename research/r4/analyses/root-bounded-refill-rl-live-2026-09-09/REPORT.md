# Four root RL updates improved this readout, but not query transfer

**Terminal, independently audited.** The fixed paired readout improved from **7 to11 correct/24**, with six wins, two losses and16 ties under the sealed terminal-endpoint definition. Query transfer stayed **0/8 before and after**. Most of the gain was on the two exposed length-transfer contexts. This is encouraging package-level evidence, not proof of adaptive planning, generalization to new source material, or a benefit from refill.

| Readout stratum | Before | After | Paired wins / losses |
|---|---:|---:|---:|
| Validation |5/8|6/8|2/1|
| Query transfer |0/8|0/8|0/0|
| Length transfer |2/8|5/8|4/1|
| All planned |7/24|11/24|6/2|

The24 pairs are nested in eight exposed context clusters, not24 independent datasets. All24 first physical root prompt-token prefixes and sampling settings match across policies. Adaptive subsequent root/child trajectories are not paired calls, and same-input sampling is not deterministic replay. The final policy is the **last committed step4**, not a best-validation selection.

## One important availability distinction

The pre-update length-transfer coordinate seed981316518 has55 HTTP200 calls, followed by the native IPython broker `set_broker_scope → _execute_silent → get_shell_msg(timeout=30)` raising `_queue.Empty`. Its trace records `is_completed=True`, but `ok=False`, `stop_condition=error`, and an empty root reply. The sealed terminal parser assigns the literal completed-empty endpoint0; training admission correctly remainsNULL. This is **not evidence of a sampled wrong final answer**. Afterward the corresponding coordinate succeeds.

Keep the frozen primary unchanged, but the availability-safe sensitivity is **five wins, two losses,16 ties, one unknown**, with net improvement bounded **[3,4]**. All other endpoints are available; all final24 are admitted. The generic symmetric sensitivity bounds in TERMINAL_DETAILS are conservative;[3,4] additionally uses the known successful after endpoint. This distinction is not a repaired primary or permission to train on the unavailable row. See the [raw excluded episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/outputs/attempt-001/readout-before/rollout/episodes/774bb96993d7761dfbe40df29bf8101b8f458f36f03be974ac9c29e40ac844b8.json").

## What actually trained

All four windows consumed exactly their mandatory first two groups. Both groups were already mixed every time. **No extra refill and no NOOP occurred.** The128 frozen candidate slots therefore yielded64 sampled training episodes;64 suffix candidates were intentionally unconsumed, not failed outcomes. All64 sampled training episodes were admitted and selected. Group successes were5+6,4+5,6+2,5+4 out of8+8 across windows. These are fresh-seed training samples, not a paired learning curve.

| Actual Adam step | Selected episodes | Root turns | Root target tokens | Gradient norm before clip | Recomputed adapter ΔL2 |
|---|---:|---:|---:|---:|---:|
|1|16|66|8,357|0.20585|0.19970|
|2|16|78|9,508|1.78960|0.14245|
|3|16|61|8,290|0.69990|0.12683|
|4|16|67|7,961|0.23356|0.10572|

Starting adapter66cce400… is the fixed low-LR success-SFT8 checkpoint, with fresh RL Adam, not the high-LR policy. Each of504 actual Adam parameter states advances1→2→3→4; moments and FP32 adapter tensors are finite. Consecutive saved adapter deltas match recorded metrics. All four input/generation/group/export/correction/state/member closures authenticate, with one policy per consumed window and all admitted members of both mixed groups included. Within-prompt advantages match independent recomputation.

The272 root turns contain34,116 credited current-action tokens. Exact native/physical root token IDs, compact processed behavior logprobs, prefix masks and checkpoint aliases agree. All prior root actions, observations and child actions are masked; recorded child/observation loss tokens are0. The child remains fixed c32de with request-local typed grammar; root actions remain unconstrained. Frozen same-forward token-TIS math is reused for one full-batch step per fresh generation, with no guard failures. No scripted operator or qualification likelihoods enter training. Optimizer computation totals177.138s; this is distinct from collection, loading, saving and total wall.

Final adapter SHA: `2286be3f7c0c9cc0e22c8ef8e3473b7d8eb6ec4b7a789ca380a0af9d3b944c71`, at [checkpoint4](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/outputs/attempt-001/window-04/training/checkpoint-4/state.json"). The unchanged RNG member SHA across actual steps is recorded, not treated as a failure: this numerical path need not consume RNG after initialization. No-op preservation has earlier fixture evidence only; it was not exercised here.

## Coverage improved; correct use of returned maps remains a bottleneck

All24 episodes use the helper before and after. Going beyond the literal first-four example rises19→21/24. Complete relevant-record request/valid-map coverage rises18→21/24, or710→842 of864 relevant record occurrences. All171 pre-update and96 post-update helper maps are complete, duplicate-free canonical maps for their respective requested IDs. Their semantic labels are not perfect:1,031/1,112→1,017/1,084 correct label occurrences. These are adaptive, differently selected calls—not a paired child-quality estimate.

A conservative native-final-branch diagnostic recognizes full relevant maps in five before and four after episodes. It only counts plain map observations whose values match actual child returns; nonrecognized output remains partial/unknown, not evidence that no usable information existed. Four before and four after wrong endpoints had a complete visible map whose implied aggregate was correct. Examples after training:

- Query-union seed981316515 still says `Answer: 7` where the visible child map implies the correct6; [native episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/outputs/attempt-001/readout-after/rollout/episodes/e302a42b69462fa36792a1d1a804d67aeeab94fc990bfd7ecfb99fa589ed3d5a.json"). The second query-union seed repeats this failure.
- Validation seed981316507 identifies the two correct records but surrounds `Answer: 2` with prose, failing the strict whole-reply contract; [native episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-bounded-refill-rl-v1/outputs/attempt-001/readout-after/rollout/episodes/29a45f8290a527cfd87a2d1447176b9d97134150cfd34397b463cf99597c550a.json").

Thus protocol validity, map semantic correctness, coverage and map→count/format failures remain separate. Strict syntax improves17→21/24; there are still ten syntactically valid but numerically wrong final answers after training. No sampled code was executed during this audit.

## Costs and release

| Returned physical usage | Before24 | After24 |
|---|---:|---:|
|Root calls|197|83|
|Child calls|171|96|
|Logical input tokens|674,375|215,468|
|Output tokens|33,064|21,206|
|Reported cached input tokens|641,520|189,888|
|Reported uncached input tokens|32,855|25,580|

All retained1,071 campaign HTTP attempts returned200:552 root and519 child. There are no request-only records and no unknown usage counters. These are physical attempts, not automatically distinct inference samples or retry-free trajectories. The all-readout cost drop includes the problematic55-call initial trajectory and other changed behavior. On the five jointly correct pairs, calls instead rise37→44 while output tokens fall4,343→3,741; do not claim uniformly cheaper correct solutions.

Scientific wall was2,127.283s; parent work was2,127.852s, exit0/no timeout, under the3,630s outer limit. Five service stages have authenticated release records confirming captured owned identities exited and ports were free; parent GPU-after-exit list is empty. The normal-path final reserve succeeded. Parent wait is outside these work clocks. Fresh96 is a separate successor and is not included in the result.

## What changes next

This run supports testing whether modest root RL can improve coverage/output discipline from this SFT warm start. It does **not** support a refill advantage: the extra sampling branch never ran. Query transfer0→0 and map→count failures argue against simply extending training and calling it adaptive generalization. The smallest discriminating follow-up is a separately frozen replication/readout that keeps the root and child fixed while comparing explicit executable aggregation support with the current map observation contract, preserving strict answers and physical costs. A separate fixed-sampling versus bounded-refill comparison is necessary if refill itself becomes the research claim. Neither is launched or selected by this audit.

## Reproduction and independence

The [METHOD](METHOD.md) was sealed postlaunch but before this auditor read outcomes—not a prelaunch preregistration. [terminal_audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: terminal_audit.py") ran once after MAIN's terminal trigger and caches completed native/checkpoint proofs. [terminal_details.py](../../../../ARTIFACTS.md#unpublished-files "Not published: terminal_details.py") adds descriptive map/cost/lifecycle analysis using the authenticated earlier independent map parser. The auditor did not author bounded-refill scientific implementation, but contributed prior shared harness/training machinery and reviewed its integration. Implementer aggregates are crosschecks, not the authority for the reported endpoints.

[METRICS](../../../../ARTIFACTS.md#unpublished-files "Not published: METRICS.json"), [128-candidate ledger](../../../../ARTIFACTS.md#unpublished-files "Not published: CANDIDATE_LEDGER.json"), [48-readout ledger](../../../../ARTIFACTS.md#unpublished-files "Not published: READOUT_LEDGER.json"), [terminal details](../../../../ARTIFACTS.md#unpublished-files "Not published: TERMINAL_DETAILS.json"), stage/checkpoint/map ledgers and FINAL_MANIFEST provide exact paths/hashes. Original science, admissions, method, sources and outputs remain untouched. No GPU, model, network, runtime fixture, service or process-control action was performed by the auditor.
