# Fixed-output visible-reference48: independent completed audit

## Result

Misleading visible source IDs strongly impair displayed-record classification even when the requested output tags and exact decoder are held fixed. Matching visible IDs are **not necessary** for high performance in this panel: unrelated visible IDs perform similarly to aligned IDs.

| Visible-reference condition | Strict correct / 768 planned labels | Accuracy | Native finals / 16 | Complete tag/shape contracts |
|---|---:|---:|---:|---:|
| Aligned | 610 | 79.43% | 16 | 16 |
| Wrong: tag names another visible record | 289 | 37.63% | 16 | 16 |
| Unrelated: visible IDs are absent from requested tags | 620 | 80.73% | 16 | 16 |

Primary aligned−wrong is **+321/768 = +41.80 percentage points**, positive in all 16 paired contexts (15–27 more correct labels per 48-item context). Wrong−unrelated is −331/768 = −43.10 points, negative in every context. Aligned−unrelated is −10/768 = −1.30 points: aligned wins 2 contexts, ties 6, loses 8. This small secondary difference is not an equivalence test or evidence of unrelated-ID superiority.

There are no NULLs, length-capped responses, invalid contracts, wrong-route completions, or reachable verifier exceptions. Strict bounds collapse to the reported values; shape-only semantic scores are identical to strict scores. All 2,304 returned tags match the required tags and order. No entire 48-item batch is semantically perfect. All independently compared endpoint scores, predictions, validity fields, and tag fidelity agree with retained producer results; no primary was repaired or replaced.

## Paired context evidence

Each row is one paired context cluster, not 48 independent experimental replicates. There are 16 clusters, four per genre, and one fresh paired seed per cluster. Genre and item summaries are descriptive; no item-independent significance claim is made.

| Context | Genre | Aligned | Wrong | Unrelated | Aligned−wrong |
|---:|---|---:|---:|---:|---:|
| 0 | government | 37 | 20 | 38 | 17 |
| 1 | government | 39 | 15 | 39 | 24 |
| 2 | government | 40 | 23 | 40 | 17 |
| 3 | government | 43 | 16 | 44 | 27 |
| 4 | slate | 37 | 17 | 37 | 20 |
| 5 | slate | 37 | 19 | 37 | 18 |
| 6 | slate | 40 | 19 | 41 | 21 |
| 7 | slate | 37 | 17 | 36 | 20 |
| 8 | telephone | 31 | 12 | 31 | 19 |
| 9 | telephone | 36 | 16 | 39 | 20 |
| 10 | telephone | 40 | 14 | 41 | 26 |
| 11 | telephone | 38 | 18 | 39 | 20 |
| 12 | travel | 36 | 21 | 37 | 15 |
| 13 | travel | 38 | 20 | 38 | 18 |
| 14 | travel | 42 | 22 | 41 | 20 |
| 15 | travel | 39 | 20 | 42 | 19 |

Genre totals (each /192), aligned/wrong/unrelated: government 159/74/161; slate 151/72/151; telephone 145/60/150; travel 155/83/158.

## Wrong-reference diagnostic

Only wrong-arm positions where the displayed record and the record named by the requested tag have different gold labels enter this predefined diagnostic. Of 530 such positions:

- Named-record gold label: 362 (68.30%).
- Displayed-record gold label: 106 (20.00%).
- Third label: 62 (11.70%).

Named-label matches exceed displayed-label matches in every context. The remaining 238 positions have coincident displayed/named gold and cannot distinguish the interpretations. This is final-output evidence consistent with misleading reference binding, **not a trace of the model's internal lookup algorithm**. There are no tools, executed programs, acquisition actions, or reasoning traces to authenticate here. No “named gold” is invented for unrelated IDs.

Auditable examples, zero-based positions in context 0, wrong call `94edfdd1d951d0a210fe2b27d3a3c7c8179a18317aa947ca362d7b8c3598f35c`:

| Position | Displayed ID | Requested tag | Returned label | Displayed gold | Named gold |
|---:|---|---|---|---|---|
| 0 | `m182a98892e3b` | `m4ba25cb0d459` | entailment | entailment | neutral |
| 1 | `m2e677825b227` | `m4f8bc8354c04` | contradiction | neutral | contradiction |
| 37 | `me6af209930a2` | `m5df56ccdaa7c` | neutral | contradiction | entailment |

These illustrate displayed, named, and third outcomes respectively; they were selected after the aggregate audit for illustration, not for primary scoring or subsequent source selection. Raw REQUEST/RESPONSE/RESULT artifacts are under the scientific attempt's `rollout/calls/<call-id>/`.

## Actual wire, provenance, and admission

Science: `sidecars/leaf-mnli-fixed-output-visible-reference-v1/outputs/attempt-001`, relative to `/project/alex_phd/runs/rlm-research-r4`. READY SHA `22c5636206757747bb4f147904a4fd49c32ca418960bfced1c59054e97fd39b6`.

The audit reran the frozen source closure and all 48 actual tokenizer-prefix/schema checks. All three members of a context have identical requested tags, exact positional JSON grammar, non-ID input fields, instructions, sampling, native input token count, and model. Only visible input IDs vary. The common question explicitly requests the relation of the **displayed hypothesis to displayed premise**, prohibits deriving labels from position/ID/tag, and orders output by displayed record. The grammar fixes 48 tag-then-label objects and each requested tag, with three canonical relation labels; it does not provide gold labels.

Actual released Qwen3-4B-Instruct-2507 revision `cdbee75f17c01a7cc42f958dc650907174af0554`, no LoRA, manifest SHA `19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f`. Actual vLLM 0.28.0 config, endpoint descriptor, and live preflight agree: BF16, context 8192, four sequences, prefix caching disabled. Default template SHA `64f85b198065d0fba2a81f37e10ed68161ce2c19a754c7100e67e0ca2ee9c326`; thinking disabled; final-only classifier and no tools. Temperature .5, top-p 1, top-k −1, maximum 3072 new tokens; seeds `981624101`–`981624116`, one per context. Actual inputs 3464–4325 tokens; largest input plus cap is 7397 <8192.

Every on-disk request's exact ordered body/hash and expected prefix matches frozen inputs. Every raw response has the actual expected model, single assistant branch, identical native prompt tokens, decoded native completion text, token-count-consistent usage, and `finish_reason=stop`. Native availability is independently established, not inferred from owner completion or HTTP 200 alone. Union harvesting found exactly 48 physical calls and no unmatched directories; all 177 retained attempt files were hashed after closure. The known latent non-string-tag scorer defect was not reached; no repairs were needed.

DATA/PUBLIC bytes equal the preceding new-context-alien panel; data SHA `e337746a0e0e057fa789c8a9b48a4aff3a81e54e193ddcd6bc0335fd79d20eec`, ancestor selection SHA `d9856c7936977f43d12c10301b675258bba3cf3c4c7795d5f695a31591fdb088`. All 16 contexts were retained without outcome selection. This is an **exposed-panel, adaptively chosen mechanism experiment**, not pristine confirmation, and no pretraining-unseen claim is made. Aligned/wrong control visible-reference presence and tag inventory; wrong/unrelated additionally change whether requested tags refer to any visible ID and the corresponding token repetition structure. Equal input-token counts and fixed grammar do not imply equal complete autoregressive outputs, FLOPs, or an isolated internal cognitive mechanism.

The auditor did not author this study but contributed shared ancestor MNLI/native/lifecycle components. METHOD_READY SHA `81f177b39bd3526007706665a5bfb22e26c3a307e3c629b209d37d10155b2e11` and PARSER_READY SHA `8ff7c2581269bba94e2de40e0da4369c0ada2b39813e1424903de2e6dd05736f` precede launch. MAIN supplied lifecycle/counts only before this audit; outcome reads started after the terminal relay. The unchanged sealed parser completed successfully in 7.03 seconds CPU wall time. No sampled code or model execution occurred during audit.

## Physical costs and operational closure

| Arm | Physical / returned / usage-known | Input tokens | Output tokens | Median request wall seconds |
|---|---:|---:|---:|---:|
| Aligned | 16 / 16 / 16 | 62,221 | 15,244 | 22.29 |
| Wrong | 16 / 16 / 16 | 62,221 | 15,322 | 22.41 |
| Unrelated | 16 / 16 / 16 | 62,221 | 15,254 | 22.36 |
| Total | 48 / 48 / 48 | 186,663 | 45,820 | — |

Zero unknown usage and zero reported cached tokens across all calls. Observed total tokens: 232,483. Provider billing remains unknown. Request latencies overlap under concurrency and must not be summed as elapsed GPU time. Collector wall time 269.502 s; owner 306.747 s; outer parent 309.494 s, exit 0, not timed out, no retry, empty GPU after exit. COMMAND epoch `1789014670.9969695`; all owned process identities exited and ports were free in `SERVICE_STOPPED.json`. OWNER_TERMINAL SHA `989dd16507f972b13b3e515db091a0e776cb6fe6ed6aa55568e181c40d7f6f87`. Parent receipts are under `operations/2026-09-10-after-dose-readout-fixed-output/attempt-001/mnli_fixed_output_visible_reference48/`.

## Queue implication

Promote the narrow finding: **a misleading source-reference field can redirect semantic predictions despite perfect output syntax and equal-length, fixed-tag controls**. Revise any stronger account that source-aligned output IDs intrinsically enable NLI: unrelated references retain performance here. Do not spend another immediate run merely repeating this exposed panel. Prefer the already running intended-interface RLM8B reachability comparison; if correspondence remains a priority afterward, a genuinely different task/source family or a minimally changed disambiguation instruction would be more informative than another tag inventory replication. No new implementation or launch is authorized by this report.

Machine-readable independent endpoints, context differences, bounds, service admission, errors, producer comparisons, and costs: `AUDIT.json` SHA `1e9136d19d104e32a8fcf38f383c747324f8eaab1e180644c3f8d0710a470a1f`. Raw artifact closure: `OUTCOME_PINS.json` SHA `46c370d6d0928b4ee33e1bd09febc75f4e1fbfca1c9069f545f408791ec9e6fe`. `FINAL_SEAL.json` binds this report, the prelaunch method/parser, source inputs, all raw artifacts, and explicit parent receipts.
