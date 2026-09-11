# Root interface SFT: independent training/readout audit

The fixed four-update SFT continuation is technically intact and teaches actual child-interface use, but does not establish useful task-performance improvement. Child use rises0/24→24/24 episodes; strict accuracy is1/24→2/24, while valid final-answer syntax falls19/24→9/24. Twenty-two first actions reproduce the taught four-record example rather than a complete task solution.

Independence boundary: this auditor did not author the SFT data, training or collector. I did author parts of the shared runtime and typed-child hooks, and reused the pinned common causal-graph checker. This is an independent audit of the SFT intervention and raw readout, not independent validation of every shared harness component. Main's METHOD was written before training/readout outcomes and is unchanged. The run became fully terminal during initial source inspection; both releases and operation EXIT were confirmed before raw readout analysis. No new training, model calls, GPU controls, source changes or host execution of sampled code occurred.

## Training integrity

Original READY397f3ccc and accepted local-runtime variant77df23b8 source/input closures authenticate. The initial adapter is historical `473210b18c4be163cd46a894614cb14934a7908e45bd97f96720928a7770ccdd`; fixed final4 is `efab2913e7fe9f5f9b381ae6eb67bb56071070f86b237e6145f98654816aad64`, config `d665754d496ad234fd441cfb340d2f597a8f13e7763a3f0592bf28720ef85a57` at `sidecars/root-interface-sft-local-runtime-v1/outputs/attempt-001/training/checkpoint-0004`. No validation-selected substitute was used.

All32 rows have exact current-action-only labels, all prefix labels−100, one EOS151645, no truncation, and lengths≤8192. Decoded targets independently equal16 authored helper actions and16 terminal answers grounded in saved actual metadata observations. No child answer tokens receive SFT credit. Each example occurs twice in the exact declared shuffled order:64 exposures,3,206 target tokens. Per epoch1,520 target tokens teach the initial helper action and only83/1,603 (5.18%) teach final answers. These are interface/metadata demonstrations, not complete semantic counting trajectories.

| Update | Actual Adam step, all504 states | Saved epoch/cursor | Adapter L2 change from start | Batch NLL |
|---|---:|---:|---:|
| 1 | 1 | 0/16 | 0.402563 | 0.331083 |
| 2 | 2 | 1/0 | 0.676610 | 0.207099 |
| 3 | 3 | 1/16 | 0.947949 | 0.076019 |
| 4 | 4 | 2/0 | 1.169540 | 0.012019 |

Every saved checkpoint's file closure, FP32 finite adapter tensors, Adam step/cursor, lr1e−4/weight-decay0 and torch/CUDA/Python RNG states were checked on CPU. Fresh Adam/RNG seed981284002, bf16 frozen base and root-LoRA-only updates are enforced by the inspected training source; load audit reports exact504 starting adapter tensors. There is no independent saved base-weight snapshot. Source clips gradient norm at1; reported pre-clip norms2.7785,2.0316,1.5657,0.5955 are finite. Batch NLLs use differing shuffled examples and are not held-out performance. Training31.6499s, total training process51.2062s; helper model was neither loaded nor updated by training.

## Raw primary endpoint

All48 planned episodes are observed and episode.ok=true, with no trace errors or setup/finalize exclusions. Completed empty/malformed/wrong output is0, not NULL; missing/incomplete/provider-unavailable would remain NULL. All scores were reconstructed from raw replies and last root availability and match collector rows. No numeric-only rescue is applied.

| Readout stratum | Pairs | Initial correct | Final4 correct |
|---|---:|---:|---:|
| Validation | 8 | 1 | 1 |
| Query transfer | 8 | 0 | 0 |
| Length transfer | 8 | 0 | 1 |
| Total | 24 | 1/24 | 2/24 |

There are2 gains,1 loss,21 ties; no jointly correct pair. Initial has19 valid `Answer: N` replies, one observed empty and four other malformed replies. Final has9 valid replies, five bare-digit replies and ten prose replies. Valid final syntax is therefore materially worse. The complete paired ledger is PRIMARY_LEDGER.json; no outcome-selected policy or endpoint was substituted.

Source allocation independently rebuilds exactly896 unique groups/public records/host labels from the frozen named root-history exclusions and leaf-training-supported pool:384 SFT-training groups,192 validation,64 query-transfer and256 length-transfer. Readout clusters are four validation contexts and two each query/length contexts, with repeated seeds nested in context. These are newly allocated relative to named root history, not source-test or pretraining-held-out confirmation. Gold counts are skewed: an evaluation-informed constant1 would get7/24, a descriptive caveat rather than an executed baseline. Dataset license remains unestablished.

## What changed in the policy

Initial uses82 root model turns and zero child calls; final uses66 root turns and50 child calls across all24 episodes. Initial first Python actions parse23/24 (one has no Python action), final24/24. Every final first action invokes the helper contract;22 are exactly the taught `records[:4]` example, two are modified filter actions. Some later actions do select/cover query-relevant records, but full task execution is inconsistent.

All50 actual child invocations are source-bound, use the fixed c32de alias and exact typed grammar, return valid ordered ID maps, and are linked to native ACP calls. Label accuracy is744/800 repeated record classifications, not800 unique records. Eleven episodes cover every relevant ID; only four of those maps imply the correct target count, and two of those four still produce a wrong final answer. Seven cover exactly the relevant ID set without extra records (including global tasks, where the relevant set is the entire file).

Mapping tool observations are visibly included in subsequent root prompts in24/24 episodes (27 mapping observations). This proves available observation exposure, not causal cognitive use. Clear failures separate the remaining problems:

- Both HUM two-user-union repeats have complete maps implying the correct count6, yet return `Answer: 8`.
- Several full global maps have semantic class errors: for example NUM length transfer implies17 instead of gold18, and the root returns17.
- Some episodes stop after the example batch with prose about needing further analysis. Five give bare digits instead of the required final format.
- Four episodes contain recoverable Python tool errors, including nonexistent `synthetic user metadata` keys and an empty filtered batch. These are sampled-policy errors, not infrastructure nulls; all episodes still finalize cleanly.

## Native provenance and cost

Every initial physical root prefix matches the frozen prompt-token sequence in all48 readouts. Root grammar is absent; phases bind the exact initial/final adapters, fixed child, image8cfe and the same qualified local wrapper/store. Weights are evaluated sequentially initial then final, so phase/time effects are not randomized. Matched seeds do not guarantee identical sampled trajectories.

The reused causal checker validates all48 graphs:198 exact native prompt/completion/logprob/mask correspondences,148 root turns and50 child turns. Fifty child-call and50 child-return semantic edges agree with trusted depth. Child actions are never root-credit targets. This verification does not itself export readout data for RL or authorize training on these evaluation contexts.

Raw JSON-string wire usage was decoded, retaining cache fields omitted by normalized usage. No request-only/orphan record or unknown token usage was found; no additional retry is visible at the captured native-request level. Lower-level unlogged retries are not ruled out.

| Phase / role | Calls | Prompt | Cached | Uncached | Completion |
|---|---:|---:|---:|---:|---:|
| Initial root | 82 | 154,844 | 147,072 | 7,772 | 30,977 |
| Initial child | 0 | 0 | 0 | 0 | 0 |
| Final root | 66 | 86,847 | 81,024 | 5,823 | 8,362 |
| Final child | 50 | 57,253 | 41,184 | 16,069 | 7,325 |

Final total116 calls,144,100 prompt,122,208 cached,21,892 uncached and15,687 completion tokens. It uses fewer output tokens but more calls and uncached input; no successful-pair efficiency comparison is defined because there are zero jointly correct pairs. Cheap incorrect output is not an efficiency win.

Readout collection initial300.682s/final296.062s; scientific inclusive elapsed751.986s, operation755.335s, exit0 with owned service releases and empty post-exit GPU inventory. The new local runtime shows no finalize errors in this study; this is not an isolated runtime speedup comparison with prior operator tasks.

## Decision-relevant conclusion

Final4 is a technically valid interface-competent warm-start candidate, not a proven better counting policy. The intervention closes the observed no-child-use gap, while coverage, semantic classification, metadata access, aggregation and final-format behavior remain separate bottlenecks. Sparse terminal supervision and absence of complete semantic trajectories are important design limitations, not established causal explanations. Any RL follow-on should preserve final4 identity and honest frozen strict scoring; main owns that decision. Original frozen sources/readouts remain unchanged. Analysis artifacts and raw hash closures accompany this report; common-harness authorship is disclosed above.
