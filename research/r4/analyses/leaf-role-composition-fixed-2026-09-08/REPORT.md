# Leaf weights help a fixed routine; full-RLM transfer remains limited

2026-09-08. Additive CPU-only audit of completed role12, new-composition48,
fixed-batch5/624 calls, and fixed-batch16/192 calls. No reruns, model requests,
training-selection changes, or generated-code execution.

## Main results

| Completed comparison | Original child | Validation-selected leaf SFT |
|---|---:|---:|
| Reused development context, full RLM | 2/6 strict | 2/6 strict |
| Six new compositions, full RLM | 4/24 strict | 6/24 strict |
| Same composition coordinates, fixed batch5 | 1/24 strict; 8/24 aggregate available | 15/24 strict; 24/24 available |
| Same coordinates, fixed batch16 | 4/24 strict; 7/24 available | 15/24 strict; 23/24 available |
| Fixed batch5 canonical record labels | 1192/1536 | 1485/1536 |
| Fixed batch16 canonical record-label yield | 1068/1536 | 1466/1536 |

Strict success is exact terminal correctness for full RLM. Fixed strict success also
requires **every batch** to be a complete canonical JSON array; an otherwise completed
malformed batch makes the aggregate unavailable/wrong, not an infrastructure null.
There are no infrastructure-null or outer-budget-censored coordinates in these runs.
These unequal operational contracts matter when comparing fixed with full RLM.

The fixed-batch5 weight contrast has 15 paired gains, 1 loss, 8 ties; canonical item
changes are 319 corrected and 26 newly wrong. But part of the final gain is contract
reliability: original raw target counts are correct on **9/24** coordinates if enum
violations are ignored offline, versus 15/24 SFT. That is a diagnostic, not a rescored
primary endpoint. On the 8 pairs where both fixed arms meet the contract, strict
scores are 1→4. All fixed-batch5 arrays have the correct length; the original failures
come from 31 noncanonical labels in 31 batches.

Against full RLM on the same 24 coordinates, fixed SFT wins 9, loses 0, ties 15.
Original fixed wins 1, loses 4, ties 19. This establishes useful fixed-routine
composition headroom, not a general advantage of recursion, planning, or one harness.

Source: [independent score audit](../../../../ARTIFACTS.md#unpublished-files "Not published: RESULT_AUDIT.json"),
[coordinate-level paired comparisons](../../../../ARTIFACTS.md#unpublished-files "Not published: PAIRED_COMPARISONS.json").

## Routing and the pre-child causal limitation

All **603** full-RLM model calls (160 role +443 composition) have exactly one request
audit and one returned-result audit matched to committed ACP request IDs. Recorded
depth agrees with trace ancestry; root calls use the original alias, and child calls
use the coordinate's bound original/SFT alias. All 60 owned-container overlays have
the same pinned engine before/after hashes. All 444 committed child call edges have
one terminal-return edge: 82/47 in role12 and 178/137 in composition48.

The original adapter is the PEFT-key-converted original-weight file
`857a7ce6…`; SFT is validation-selected epoch2/checkpoint0128, `c32de129…`.
The frozen selection hash is `46025168…`. Both use the same dual-LoRA service;
its actual LoRA dtype is auto/BF16, not FP32 inference. Audit evidence verifies
forwarded aliases and bound artifact identities, not an independent per-call
inspection of GPU tensors.

All 30 pairs have identical first forwarded-payload hashes, actual trace-prefix
message hashes, and recorded sampling, including seed. Nonetheless, after removing
tool-call UUIDs, first root responses differ in **3/6 role pairs and 15/24 composition
pairs**, before any child response exists. Some differences are merely textual;
[AST sensitivity](../../../../ARTIFACTS.md#unpublished-files "Not published: FIRST_ROOT_AST_SENSITIVITY.json") is secondary and does not equate
unparseable/empty code with an executable program. The source of this request/seed
nondeterminism was not isolated here. **No pre-child difference is attributed to
child-weight mediation.** Post-hoc identical-first-response subsets score 1/3→2/3
and 1/9→2/9; these tiny selected subsets do not replace the primary comparison.

## Where the process improves, and where it fails

| Full-RLM process measure | Role original → SFT | Composition original → SFT |
|---|---:|---:|
| Episodes with committed recursion | 5/6 → 4/6 | 15/24 → 14/24 |
| Complete unique-question coverage | 5/6 → 3/6 | 10/24 → 13/24 |
| Canonical correct / aligned assignments | 356/445 → 261/267 | 517/686 → 815/846 |
| Complete canonical child arrays | 70/82 → 45/47 | 138/178 → 134/137 |
| Child Python/tool turns | 0 → 0 | 29 → 0 |

Aligned-assignment accuracy conditions on successful whole-response parsing. Planned
record opportunities are 534 per role arm and 1536 per composition arm; unclassified
records are not silently dropped from coverage. On common full-coverage pairs,
canonical accuracy is 210/267→261/267 (3 reused-context pairs) and
437/576→555/576 (9 composition pairs), also post-hoc common-support diagnostics.
These are repeated question observations, not hundreds of independent samples.

All composition child prompts preserve the six definition lines, but the exact
seven-line block is not universal. Role original abbreviation-repeat0 omits the
semantic definition lines entirely. The root can change batching, wording and
recovery, so this is not an exact leaf-request replay across every paired episode.

The [root integration audit](../../../../ARTIFACTS.md#unpublished-files "Not published: ROOT_INTEGRATION_AUDIT.json") checks all 60 traces without
executing generated Python. Among 23 fully covered composition episodes, 22
faithfully count retained child labels. The remaining failure is particularly clear:

- **Correct child target labels lost by the root:** SFT composition02/HUM/repeat1
  has 61/64 correct labels, including all14 true HUM records. At root node2,
  `batch_labels.extend(child.answer)` extends characters, then counts a whole
  label and returns0. Its original-arm first action already differs, so the paired
  loss cannot be called child-mediated.
  [Raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-composition-transfer-v1/outputs/attempt-001/episodes/7eea21d9caec13976bd381755cc1aa513e92e1fe7c81ee522b8b4fadeaa9b8a3.json").
- **Wrong intermediate process rewarded:** original composition02/HUM/repeat1
  returns the correct14 by taking first elements even from wrong-length JSON lists.
  FP records26/63 cancel FN38/53. Only46 records have strict aligned outputs,
  35 correct. One failed initial call plus63 recovery calls reaches the native64-call
  cap; record64 has no committed inference. Its gold is entity, so that omission
  happens not to alter HUM count. The non-model limit result is a pinned-runtime
  inference, not a retained model response. All29 original child tool turns occur
  in this singleton branch; children sometimes try solving questions or calling
  external APIs rather than returning labels.
  [Raw episode](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-composition-transfer-v1/outputs/attempt-001/episodes/020688150fec86d44861c6c439ed2bc7244a49059dd9394715b631cbed623308.json").
- **Development loss despite better overall labels:** original abbreviation-repeat0
  classifies all four target records correctly and gets4; selected SFT misses
  record75 and gets3, despite 86/89 rather than59/89 overall labels correct. A
  different first root action also changes the child prompt here. The
  matched-first-action abbreviation-repeat1 instead moves5→4 with76/89→88/89
  labels correct: original FP29/72 and FN75 are all repaired by selected SFT.
- **Other composition bottlenecks:** 8 original and9 SFT episodes end with
  tool-looking text that never executes; one per arm raises a root record-parsing
  IndexError before classification. Four original episodes have no aligned child
  outputs. One SFT episode replaces failed first50 labels with description
  placeholders and counts only the final14 actual classifications.

No original composition success has every record correctly classified. Only2/6
SFT successes do; the others have non-target errors. Fixed batch5 successes have
no target FP/FN cancellation, but 2/4 original batch16 successes do. Final accuracy,
target membership, whole-label accuracy and faithful aggregation must stay separate.

Detailed child input mapping, committed terminal outputs and per-record predictions:
[child record audit](../../../../ARTIFACTS.md#unpublished-files "Not published: CHILD_RECORD_AUDIT.json").

## Cost and batch size

| Condition, original / SFT | Logical input tokens | Output tokens | Run elapsed |
|---|---:|---:|---:|
| Development role12 | 84,897 /93,232 | 7,427 /13,505 | 247.65 s |
| Composition48 full RLM | 282,393 /181,657 | 46,205 /24,700 | 673.16 s |
| Fixed batch5, 624 calls | 248,804 /248,804 | 7,962 /6,721 | 54.37 s |
| Fixed batch16, 192 calls | 86,372 /86,372 | 7,351 /6,503 | 43.68 s |

Batch16 uses 65.3% fewer logical input tokens than batch5. Both SFT runs score15/24,
but one pair improves and another worsens; the same total does not imply identical
behavior. Original batch16 has 10 wrong-length arrays and SFT1, without length
truncations. Conditional aligned-label accuracy is 1068/1376 original and1466/1520
SFT, versus1192/1536 and1485/1536 for batch5; the larger primary-yield drop includes
missing-array penalties.

Full RLM uses rootless containers and 2048 tokens per model turn; fixed uses the
reconstructed native leaf system/tools, first-response-only direct Eval-compatible
calls, 256 output tokens, source-order batches, no tool execution or repair, and
deterministic host counting. Roots often choose batch10/50/64 or singleton loops.
Fixed requests never contain the aggregate query. The coordinate seeds are matched,
not the sequence of every child request. Logical input counts cached tokens once;
fixed batch5 cached input is241,824 per arm and batch16 is82,000. Elapsed times
include different concurrency/startup/overlap and are not clean GPU speedup estimates.

## Interpretation and next uncertainty

The strongest supported statement is that **role-specific leaf SFT substantially
improves classification and contract reliability, while free root execution can
lose much of the available composition performance**. It does not establish learned
planning, recursion superiority, or broad harness–weight co-adaptation.

These are six synthetic contexts containing384 predeclared clean TREC source-test
questions, two target-count queries and two seeds; component-test source overlap is
declared. Weights were selected only on validation. The development study is one
historically reused OOLONG context, not six independent contexts. The audit does not
use these test outcomes to change weights, prompts or training admission.

For the already-running root-only capture, prioritize checking train-only exact
root-action masks/behavior likelihoods and whether rewarded roots actually preserve
coverage and aggregation. Afterwards, a small **frozen first-root-action replay**
on development data would isolate child-weight effects from observed prebranch
variation. Typed/cardinality-checked child returns address a distinct contract
failure, but do not substitute for semantic labels or root parsing; preserve
train-only process verification as a separate diagnostic.

Parent-reported batch1/batch64 follow-ups are complete and **not audited in this
seal**. Keep their separate frontier audit next, including the changed1024-token
cap; do not combine them into the256-cap frontier without qualification:
[batch-extremes artifacts](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/fixed-leaf-batch-extremes-v1/outputs/").
An exact-cardinality/enum batch64 control is being prepared by the other agent.

## Reproduction and seal

`audit.py --omit-episodes` independently checks all four completed attempts;
`root_integration.py --cells` verifies the trace-grounded mechanism arithmetic.
Both are read-only, CPU-only, stdout-only. Fresh verification passed79 distinct
frozen source-file hashes,60 full-RLM episodes,603 routed/committed model calls,
816 fixed raw responses, and96 fixed aggregate coordinates. The result seal hashes
actual scoped input/output/analysis files, not archived trees or live service logs.
See [verification](../../../../ARTIFACTS.md#unpublished-files "Not published: VERIFICATION.json") and [immutable result seal](RESULT_SEAL.json).
