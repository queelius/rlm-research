# Indexed output helps; extra indexed-target training did not beat B meaningfully

**Final, independently audited.** The automatic anchor→indexed-SFT sequence completed both jobs without timeout. All600 anchor calls and624 matched HF readouts were retained. No experiment, checkpoint, acceptance, queue, or GPU process was changed by this analysis.

The most important control is B: although B was trained only on anonymous label arrays, it already scores373/384 with free indexed output. Explicit indexed-target training scores374/384—two gains and one loss. This run therefore does **not** establish a useful additional benefit from indexed-target training over the matched mixed-size B curriculum. It does establish that the input/output contract can make a large difference to usable classification results. [Independent SFT metrics](../../../../ARTIFACTS.md#unpublished-files "Not published: SFT_METRICS.json")

## The completed three-weight comparison

All weights used the same frozen prepared prompt IDs within each representation, native system/tools, HF greedy generation, and microbatch2. Fixed-five outputs had a256-token cap; long outputs had a3,072-token cap. No grammar, tool execution, answer repair, or offline fallback was used.

| Readout | Old fixed-five SFT | Mixed-size B | Indexed-target SFT |
|---|---:|---:|---:|
| Five-item anonymous, correct /489 | 473 | 476 | 473 |
| Five-item indexed, correct /489 | 0 | 475 | 476 |
| 64-item anonymous, correct /384 | 0 | 0 | 0 |
| 64-item indexed, correct /384 | 0 | 373 | 374 |
| Valid64 anonymous responses /6 | 0 | 0 | 0 |
| Valid64 indexed responses /6 | 0 | 6 | 6 |

Every fixed-five response from B and the indexed-trained model was valid, as were old's anonymous responses. Old's98 indexed fixed-five responses were all tool calls:96 complete `ipython` envelopes and two unclosed envelopes. Its six indexed64 outputs also selected `ipython`. They are invalid under the requested plain-JSON leaf contract; no generated code was executed and no labels were recovered for scoring. These zeros are **not evidence that old lacks all of the relevant label knowledge**.

Anonymous64 failed differently across weights. Old and the indexed-trained model each exhausted3,072 tokens on all six responses. B produced six closed JSON arrays with the wrong cardinality, without truncation. Thus indexed-target training did not solve the original long anonymous-array task; compared with B, it changed that failure back to costly over-generation. [All raw-readout hashes and failure counts](../../../../ARTIFACTS.md#unpublished-files "Not published: SFT_METRICS.json")

B's and the indexed-trained model's indexed64 results are almost indistinguishable in this small sample. Correct counts by successive16-item blocks are95/94/92/92 for B and95/94/92/93 for indexed training, each block out of96. Both retain late-position performance. Whole-response exactness is only1/6 for B and2/6 for indexed training, so high item accuracy is not equivalent to reliable exact aggregate answers.

On matched item outcomes, indexed training versus B has:

- Anonymous fixed-five: zero gains, three losses.
- Indexed fixed-five: two gains, one loss.
- Indexed64: two gains, one loss.

Against old on anonymous fixed-five, the equal473/489 aggregate hides five gains and five losses. These are one-seed training runs with deterministic HF readouts,489 test groups and six exposed long contexts—not a replicated estimate of a one-item training advantage. No confidence or novelty claim is warranted.

## What the separate anchor control establishes

The completed old-model anchor study used the same indexed inputs in both arms, with anonymous versus indexed output contracts and exact schemas. At64 items, TREC improved586→1,437 correct of1,536 repeated assignments; genuinely fresh SST-2 groups improved615→986 of1,024. All responses in both arms were valid, and all24 TREC /16 SST paired coordinates improved. Small batches stayed near95–96%. This is strong evidence for a representation-supported correspondence effect across different task vocabularies, not merely array-format recovery. The [anchor report](ANCHOR_REPORT.md) contains the full paired outcomes, position pattern, data provenance and limitations.

The studies should not be pooled into a single treatment effect. The anchor uses sampled vLLM calls, stable IDs and permutations, and schema constraints; the HF training comparison uses greedy calls, batch-local IDs, and free output. Within the HF comparison, anonymous versus indexed changes both input representation and output contract. Across weights within a representation, prompts are identical. The large anchor effect and B's strong free indexed result together argue for examining the model–harness contract before adding more specialized training.

## Training and identity audit

The new run used the exact original converted adapter `857a7ce6…`, not old SFT or B as a warm start. Its504 loaded adapter tensors matched disk values and dtypes exactly, with no missing or unexpected keys. Baseline load audits likewise matched old `c32de129…` and B `59ad8542…`. The final indexed adapter is `7a18736d…`. Full hashes are in the [fixed-final binding record](../../../../ARTIFACTS.md#unpublished-files "Not published: FINAL_CHECKPOINT_BINDING.json") and [actual-load supplement](../../../../ARTIFACTS.md#unpublished-files "Not published: SFT_SUPPLEMENT.json").

The independent CPU audit verified:

- Actual204 Adam steps, final epoch2/cursor0, with finite optimizer moments. Fourteen checkpoint commits exist at16,32,48,64,80,96,102,112,128,144,160,176,192,204; every state-listed file hash was authenticated, and saved metric prefixes agree.
- Each of5,065 training groups appears exactly once per epoch, in the frozen B-matched order:10,130 actual record exposures and118,198 supervised target tokens.
- Every prepared prompt prefix is masked with `-100`; labels equal the native assistant suffix, including the pinned terminator. No input exceeds8192. This is authoritative-label SFT, with no rollout reward or invented behavior probability.
- A final FP32 LoRA tensor delta of5.0347780108 from the original adapter, independently recomputed. Final saved tensors and optimizer moments are finite. The run used a BF16 base and FP32 adapter, AdamW at1e-4, weight decay0, and clipping1. The recorded gradient norms are pre-clipping norms.
- The checkpoint choice is explicitly fixed final epoch2. SELECTION precedes new-model test captures; monitored validation scores did not choose weights. Epoch1 validation was238/300 anonymous and243/300 indexed; epoch2 was259/300 and262/300, all valid.
- All624 persisted prompt-ID sequences match their prepared rows and declared per-model binding. All raw contents independently reproduce the strict prediction vectors and scores. The HF input check uses saved IDs and the pinned, qualified batching path; unlike the anchor, it is not a provider-side HTTP echo.

Saved RNG states were authenticated; no GPU resume was performed in this run. The audit tensor-diffs LoRA, not a separately saved final full-base checkpoint. The frozen training path and actual load audit establish the intended frozen-base execution boundary. [Audit program](../../../../ARTIFACTS.md#unpublished-files "Not published: audit_sft.py"), [structured results](../../../../ARTIFACTS.md#unpublished-files "Not published: SFT_METRICS.json")

## Compute and completed operation

Record exposure and update count match B, but compute does not. B has47,288 target tokens versus118,198 for indexed training, about2.5×. Padded training inputs are2,719,578 versus3,020,431, about11.1% more. Actual indexed optimization took1,282.463 seconds (21.37 minutes), versus B's recorded1,142.028 seconds. Longer targets and a different loss distribution prevent interpreting this as a compute-matched representation-only gradient experiment.

The indexed job's complete load/train/checkpoint/validation/three-weight-readout envelope took4,941.115 seconds (82.35 minutes), below its90-minute limit. Besides the624 matched readouts audited here, two epochs generated240 monitored validation responses on the same300 groups in two formats:864 HF response generations overall, plus training and validation-loss forwards. About61 minutes were outside the optimization clock; expensive uncapped-until3,072 free generations contributed substantially. Peak allocated memory was21,583,873,536 bytes and reserved memory41,395,683,328 bytes. The recorded stack was Python3.12.12, torch2.13.0+cu130, transformers5.15.1, peft0.20.0 and safetensors0.8.0 on one A10040GB full MIG.

Anchor collection took175.643 seconds; its service envelope took225.599 seconds. Coordinator predecessor waiting was1,405.112 seconds while the root run still owned the GPU; this is not anchor compute or established GPU idle time. Both jobs exited0, neither timed out, no result was censored, both owned-stage exits recorded empty GPU process lists, and no retries or analyst cleanup were performed. [Operation and actual-load records](../../../../ARTIFACTS.md#unpublished-files "Not published: SFT_SUPPLEMENT.json")

## What changes next

1. **Keep B as the decisive training control.** A new-versus-old comparison alone would mistake old's tool-mode failures for evidence that indexed-target training was necessary. The already frozen old/new grammar160 study remains useful, but an additive B-only80-call companion is the minimal control needed before making an indexed-specific transfer claim. Do not mutate accepted cells.
2. **Test grammar and tool-mode selection before more training.** The anchor shows old can classify strongly when its output is constrained. A separately declared tool-availability ablation can test whether old's free indexed failures are primarily a routing/mode problem. Do not execute or rescore current tool outputs as a fallback.
3. **Do not deploy the new checkpoint as a generic long-output fix.** Anonymous64 is still unusable and more expensive than B's short-array failure. Any RLM deployment needs a declared child input/output contract and a paired end-to-end evaluation; these component experiments do not establish better root orchestration.
4. **If testing learned identity tracking, break the position cue.** Batch-local ascending IDs may support a positional solution. Stable IDs through fresh shuffles, new source groups, and explicit coverage/cost measures are a better next discriminator than simply extending training. The [proposal](NEXT_EXPERIMENT_PROPOSAL.md) is advisory only; the parent's accepted queue remains authoritative.

The strongest revised conclusion is therefore: **explicit correspondence can expose capability that a poorly matched contract hides; in this study, mixed-size B plus indexed prompting already captures nearly all the observed benefit of extra indexed-target SFT.** This is exploratory component evidence with exposed TREC contexts, public SST validation, unknown pretraining overlap, unresolved underlying-license confirmation, few contexts and no replicated training seeds—not proof of general reasoning or a publishable novelty claim by itself.
