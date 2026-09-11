# Higher learning rate improves this paired readout, mainly on longer tasks

Independent terminal audit, September 9, 2026. **High LR solves 14/24 versus low
LR's 8/24: nine paired gains, three losses, twelve ties, no unavailable pairs.**
Final syntax rises from 16/24 to 24/24 and complete relevant helper-map coverage
from 21/24 to 24/24. Most accuracy gain is in the exposed length-transfer stratum;
query-transfer accuracy remains 2/8. This is one controlled learning-rate comparison
on the same complete-success corpus, not a new-source or independent-training-seed
replication.

The high-LR policy uses far fewer calls overall, but **not on the five jointly
correct cases**: those use 38 high versus 32 low calls. Failure-path savings must
not be presented as universal successful-task efficiency.

## What was compared

Both training runs start exact interface-SFT efab weights with fresh Adam and use
the same 27 confirmed training-only trajectories, 114 native root actions and
15,256 target tokens per pass. Eight identical ordered full passes give 122,048
target exposures. The private adapter changes exactly two numerical LR literals
(optimizer creation and restoration assertion) from **2e−5 to 1e−4**, a fivefold
increase. Loss, masks, precision, clipping, optimizer recipe, seed, source rows,
recovery actions and fixed-final-eight rule are otherwise unchanged. The readout
uses fresh paired seeds 981314101–108/201–208/301–308, the same 24 task/prompt
coordinates and fixed typed child c32de, sequential services low then high.

| Arm | Fixed final8 adapter SHA256 |
|---|---|
| Low, existing complete-success SFT | `66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5` |
| High, new complete-success SFT | `0ba42364183a311a8f5b67e4bac4e9294924c1dfb73f152a209811df09b78773` |

Actual phase checkpoint bindings, not alias strings, identify treatment: the root
alias is reused across the separate services. Neither checkpoint was selected
using these outcomes. Their saved config bytes differ only in permutation of the
same seven `target_modules`; there is no changed target-module set. Both use the
same BF16 base and FP32 rank8 adapter. The comparison intends one LR change; it
does not claim bitwise identical floating-point training aside from that change.

## Primary and secondary endpoints

| Metric /24 | Low | High |
|---|---:|---:|
| Strict whole-reply correct | 8 | 14 |
| Strict final syntax | 16 | 24 |
| Completed protocol failure | 8 | 0 |
| Valid syntax, wrong number | 8 | 10 |
| Completed empty reply (included in failure) | 1 | 0 |
| Availability NULL / unrun | 0 / 0 | 0 / 0 |
| Exact first taught HELPER copy /24 AST-valid actions | 22 | 22 |
| First helper requests exactly the first four IDs | 22 | 22 |
| Helper used | 24 | 24 |
| Requests beyond the first four | 21 | 24 |
| Complete relevant valid-map coverage | 21 | 24 |

High-minus-low has nine wins, three losses, twelve ties and zero unknowns; net
planned-denominator bounds are both +6/24 (+25 percentage points). There are eight
source-context clusters, not 48 independent trials. Every pair's first physical
prompt and sampling settings match; adaptive trajectories need not match.

| Stratum, eight cases each | Low correct | High correct | Net |
|---|---:|---:|---:|
| Validation | 5 | 6 | +1 |
| Query transfer | 2 | 2 | 0 |
| Length transfer | 1 | 6 | +5 |

Three context clusters improve, one declines, four tie. Both length clusters
improve (0→2/4 and 1→4/4). Query-transfer-00 remains 0/4 for both despite high's
complete relevant coverage. The other query cluster has two gains and two losses,
not identical trajectories behind equal totals. The changed method is not a
reliable universal task improvement established by this small run.

All 48 outputs were independently reconstructed under the frozen strict ASCII
whole-reply rule; completed empty is zero, never NULL. No repair, permissive
number extraction or endpoint-admission reinterpretation was applied. No fatal
episode/native-graph failure, request-only tail or missing usage appears.

## Training and native evidence checks

All eight new checkpoints authenticate their actual adapter/config/Adam/RNG members,
contiguous previous-state hashes, full-pass cursor0 and epoch=step. Every saved Adam
has 504 finite FP32 moment states at the exact step1…8, LR1e−4, betas .9/.999,
eps1e−8 and zero weight decay. No child was loaded or updated. A single invocation
and no resume completed the eight updates; the exact-start load audit has all504
adapter tensors/dtypes equal, no missing or unexpected keys.

Independent CPU tensor differences agree with reported deltas at every step.
Final high delta from efab is **1.764312391**, with last-step delta0.190381045;
final high-minus-low tensor L2 is1.420995053. Nonzero parameter movement is not
evidence of useful learning by itself. All saved RNG bytes remain identical across
the eight steps, consistent with this no-dropout loop's externally deterministic
Python shuffles; RNG artifact identity is checked, not inferred from seed names.

The exact corpus bytes match the previously native-authenticated teacher corpus;
its 27 graphs/114 root suffixes are an authenticated prior proof, not new evaluation
teachers. Direct mask checks preserve physical input IDs, current-root labels,
processed old logprob lengths and all114 native terminators151645. Child/tool/history
tokens are masked. Teacher likelihood is provenance only in supervised CE.

Every pass's 114 FP32 coefficients, target counts, episode/turn order, weighted CE
and separate token NLL reconcile. Loss is equal episode→equal root turn→mean
current action CE, not global target-token mean. Coefficient masses and CE
contributions are **not gradient shares**. Initial weighted CE is identical to the
old run,0.061086; final high CE is0.040527 versus low0.052086. Final high token NLL
is0.061771. Intermediate-root CE falls1305.90→933.31; last-root CE is already very
small at0.0000567. That does not establish which learned transition caused the
new final-format gain, nor prove a particular reasoning mechanism.

All **648 physical calls** (350 root,298 child) reconcile their native/wire prompt
IDs, sampled IDs/logprobs, trusted role, actual model binding and full-support
temperature0.5 sampling. The common local runtime/image, source-bound typed child
schema, unchanged root tools/prompts and first-prefix equality authenticate.
All298 typed maps are complete, duplicate-free canonical maps for their requested
IDs. Their observed semantic label occurrences are1256/1324 low and1018/1084 high;
these repeated, adaptively chosen labels are not a paired estimate of changed
child capability. Child weights never changed.

## What remains wrong after stronger training

Unchanged initial-copy frequency but greater later coverage and fewer total calls
points to changed behavior after first uptake, not proof of improved first-action
planning. Valid maps and full coverage do not guarantee a correct answer.

The conservative final-branch diagnostic recognizes complete supported maps in
eight low and three high episodes. Five and three respectively imply the correct
target count. Most other episodes print numbers or other structures rather than
a standalone full map, so they are diagnostically partial—not lacking coverage,
endpoint NULL or automatically wrong.

Two high examples retain a clear map→count failure: seeds981314207 and981314208
have complete native-supported maps implying6, equal to gold, but both end
`Answer: 8`. Low is correct on both, so these are real regressions.
[First high example](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-sft-lr-v1/outputs/attempt-001/high/rollout/episodes/2dd7219477e6a950f850923cb24e508909260a81fec54d0994df8bedd15d8920.json"),
[second](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-sft-lr-v1/outputs/attempt-001/high/rollout/episodes/1cd97a72f64532e219e7957e3864d53d784ef273133305fa3b3dc64ea47b2742.json").

Conversely seed981314102 low has a correct complete map/count3 but surrounds the
answer with prose, failing strict output; high succeeds. Low seed981314302 has a
correct supported map/count1 but emits `24`; high succeeds. Gains therefore mix
format, coverage and numerical-content changes—not pure semantic classification.
[Low format example](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-sft-lr-v1/outputs/attempt-001/low/rollout/episodes/ea99aeb2467210bde57373487c302a07d13d12d057a786f0fd88223251696ea5.json"),
[low counting example](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/root-success-sft-lr-v1/outputs/attempt-001/low/rollout/episodes/76209c56768524bae2e9c44c28e7642a781eb04d630a282576ccd318458fa787.json").

## Costs and operational lineage

| Readout quantity | Low | High |
|---|---:|---:|
| Root / child calls | 255 /234 | 95 /64 |
| Root input / output tokens | 761598 /26644 | 139029 /12454 |
| Child input / output tokens | 213076 /12514 | 74689 /9927 |
| Total cached / uncached input | 938528 /36146 | 189408 /24310 |
| Collection seconds | 414.162 | 289.748 |

Across all24 paired cases, high uses0.325× calls and0.572× output tokens. On the
five jointly correct cases it instead uses **38 versus32 calls**,5295 versus3647
output tokens, and3670 versus5410 uncached input tokens. These successful-case
costs do not support a blanket efficiency claim. Cache counters are all known but
are not GPU FLOPs; summed parallel episode seconds are not elapsed job time.

High training records589.929 cumulative load/verification/optimization/checkpoint
seconds, one invocation/no resume, peak allocated memory14,452,734,464 bytes.
The science terminal completes in1399.086s; the actual v2 parent exits0 after
1399.630s with no timeout and GPU process list empty. Both phase collectors exit0
and both captured owned-process release markers pass.

The first parent was accepted but failed schema authentication **before START or
any training/model call**, owing to missing `predecessor_evidence_sha256`. Its
unchanged PLAN/ACCEPTANCE remain. The additive v2 parent restores only that required
mapping. It does not resample a failed study or change scientific inputs. This
cause is documented by MAIN's retained v2 REVIEW and the absent original START;
the auditor does not invent an unavailable original process-duration trace.
Actual operation: `operations/2026-09-09-after-phase192-highlr48-v2`.

## Decision-relevant interpretation and limits

Under this exact corpus/start/seed/eight-pass recipe, stronger optimization is a
useful signal: strict accuracy, final format and coverage improve, especially on
the two longer exposed context clusters. This is more directly controlled than
comparing unrelated training packages. It is still one training realization and
24 paired generations over eight exposed clusters, with sequential phase order,
shared teacher/child histories and unknown public pretraining overlap.

The next useful test would independently replicate the LR contrast or test faithful
post-observation aggregation/query selection—not simply increase LR again based on
this sample. Query performance stayed flat and exact-map wrong counts persist.
Keep existing low-LR-start RL approval unchanged; this readout does not retroactively
choose its starting policy. No unseen-task, generic planning, novelty or population
superiority claim is established.

## Reproducibility and handover

Original METHOD/METHOD_INPUTS/METHOD_READY are byte-identical. HANDOVER describes
the analyst switch and shared-harness authorship. Two focused handover fixtures
pass; the independent SFT72 native/endpoint/Adam audit is reused with only paths,
two arms and intended LR assertion changed. Preparation added an authenticated
older prompt manifest absent from the direct high-LR source map; no outcome rule
changed. No implementer aggregate score was imported as authority.

AUDIT.json retains each raw path, physical proof, strict pair and training state;
DETAILS.json contains context/cost/map/loss-position diagnostics; TENSOR_CHECKS.json
contains bounded actual saved-tensor/moment checks; METRICS.json and FINAL_SOURCES
provide compact results and exact lifecycle/provenance. FINAL_MANIFEST seals the
analysis. No accepted sources, outputs, masks, services or GPU state were altered.
