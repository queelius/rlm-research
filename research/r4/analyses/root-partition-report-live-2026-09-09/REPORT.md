# Independent partition-pilot audit — final

2026-09-09. Decision: do not promote a communication-loss or recursion-benefit claim. Exact evidence acquisition worked; the readout is confounded by output caps, JSON-format failure and residual semantic omissions. Calibrate the final-answer interface at a sufficient cap before further report-composition experiments.

## Primary results and failure accounting

Independent reconstruction agrees with all five reported strict accuracies:0/8. There are four engineered worlds and four partition pairs, not eight independent worlds. All88 planned calls and40 final outputs are retained; no missing/request-only/error/extra calls, retries, or unknown token/latency measurements.

| Endpoint arm | Strict correct | Valid final JSON | Length at cap | EOS stop | Gold array inside prose, diagnostic only |
|---|---:|---:|---:|---:|---:|
| Ordinary reports |0/8|7/8|1/8|7/8|0/8|
| Full evidence |0/8|0/8|8/8|0/8|0/8|
| Lossy local winners |0/8|0/8|8/8|0/8|0/8|
| Direct256 |0/8|0/8|8/8|0/8|0/8|
| Direct2560 |0/8|0/8|0/8|8/8|4/8 =2/4 unique worlds|

Availability means an actually retained generated text here; malformed/length outputs fail the frozen strict parser, not missing-data NULL. There are33 malformed finals and7 valid-but-wrong finals. Full-minus-ordinary has0 wins,0 losses,8 tied failures, with4 ties in each partition and no unavailable comparisons. Every arm has0/4 worlds correct under both partitions. Ordinary answers flip in all3 worlds with valid answers under both partitions; world3's co-located answer is truncated, so its strict answer flip is unavailable. Other arms have no valid strict-answer pairs; equality of two parse failures is not answer agreement.

All direct prompts, seeds and generated token IDs are identical between the two partitions of each world. Thus the eight direct calls per cap are physically paid, but provide only four unique realizations. Every256-token direct output is exactly the first256 tokens of its2560-token counterpart. The larger-cap outputs end naturally at973/580/1154/748 tokens for worlds0/1/2/3, respectively, but retain prose and fenced JSON despite the JSON-only instruction. Their single valid embedded-array candidates are correct for worlds0/2. World1 omits c02,c04; world3 omits c01,c02,c07,c08,c10. These are genuine residual semantic omissions, not just strict-parser penalties. Extracting embedded arrays is diagnostic only and never repairs primary accuracy.

## Actual children and delivered reports

All24 extraction calls stop naturally at227 generated tokens, produce exactly16 unique original triples, and have precision=recall=1.0 with no unsupported, missing or duplicate triples. All384 emitted triples are correct (the same192 world records recur under two partitions). Full report projection is independently rebuilt from these exact raw arrays and implies gold on8/8 coordinates. Lossy projection implies gold on4/8 co-located coordinates and yields[[],[],[]] on all four cross coordinates. The cross loss is engineered by the partition, not discovered neural evidence.

All24 ordinary child texts were read in full.21/24 hit the768-token cap; the other3 stop at624,724,767. They repeatedly describe missing chunks and local non-overlap, but also transmit positive A-buyer/B-buyer facts and explicitly recommend their global intersection. The frozen ordinary-report contract has no trusted symbolic implication parser; this audit does not introduce one.

A separately labeled manual annotation selects the positive current-chunk A/B lists in all12 cross reports, with exact raw-text excerpts and call hashes in DIAGNOSTICS.json.11/12 selected lists exactly match the source sets. The remaining report, world3-cross-ordinary-0, omits c09's A purchase while claiming c09 bought only D; c09 has no B globally, so this omission cannot change the join answer. Unioning the annotated A sets and B sets and intersecting them recovers the correct answer in all4 worlds. This is positive evidence that query-sufficient facts survived the ordinary channel, not a claim that the entire prose is unambiguous or that a model used these facts.

Nevertheless, cross ordinary parents return[],[],[],["c06"]. Co-located ordinary returns all12 IDs in world0, ["c02","c04","c08","c12"] in world1 (omitting the explicitly reported c05), and six of seven correct IDs in world2 (omitting explicitly reported c01); world3 truncates while rereading records. These are not successful compositions. Local-no-overlap emphasis or report-following is a plausible hypothesis, but the pilot does not distinguish it from attention/instruction interference or general synthesis errors.

All16 full/lossy parent texts were read. Each starts verbose enumeration of the original records and truncates at256 before any answer. Original records are present in every actual parent message; parent blindness cannot explain the floor. There is no evidence of executed Python or symbolic report reduction: this is fixed one-level HF generation, not an autonomous RLM/IPython run. Complete evidence with truncated parent prose establishes an interface/cap bottleneck in this instrument, not inability to compose with sufficient budget or a useful report-choice effect.

## Native and provenance audit

The original outcome-blind METHOD_READY SHA256 is5ee936d06d5f68ecc24c79f825fc2d2a29aca839b98428a22974d29915cd65dc. Its author also wrote the collector, as its own METHOD states. This later auditor did not author the collector; it independently executed the separately written ordinal oracle and rebuilt prompts, projections and raw scoring. The added METHOD_EXTENSION explicitly records MAIN's prior aggregate/partial-outcome exposure and does not claim to be outcome-blind.

Verified the original method/source closure; independently regenerated all records, RNG order,3×16 partitions, gold sets of sizes3/5/7/9, original parent ordering and paired sampling seeds. Verified all64 static request objects and all24 dynamic parent report serializations against actual requests. The dynamic messages preserve original records and exact uncorrected raw reports; no host gold is inserted. All88 native prompt token arrays, assistant-generation suffixes, output counts, EOS termination, raw decoding and content decoding match independently rendered cached-tokenizer values. Every non-EOS generation exactly hits its cap. No generated code was executed.

Actual binding is released Qwen3-4B-Instruct-2507 revision cdbee75f17c01a7cc42f958dc650907174af0554, without a research adapter. MODEL_LOADED records Qwen3ForCausalLM, BF16, SDPA, CUDA13.0, A10040GB MIG7g.40gb and a3.3965s cold model load. Accepted prior full shard hashes and current immutable size/mtime/inode identities match; this audit does not claim a second full8GB shard rehash. Tokenizer/config and qualified generation-source files were rehashed. Actual call kwargs override model defaults with temperature0.6, top_p0.95, top_k0, repetition_penalty1.0 and use_cache=True. Child cap768, short/parent cap256, expanded cap2560; no grammar or training.

Parent RESULT has exit0, no timeout, GPU PID list[], job wall1325.5525s. Science STATUS elapsed1324.5781s includes startup. Parent's1625.6759s total includes300.023s predecessor waiting, not extra pilot inference. Outcome and parent artifacts were hashed before raw-value parsing and remained unchanged through sealing:
- STATUS SHA256:f55f793108021f26cab82d133c1f4557717c1a5c4914c272752b0f1b73101952.
- OUTCOMES SHA256:f9d0d0630d2ff927fad35728a39090d7b6ab8c7c01b1f63c773d92ba2709cafb.

## Costs

Physical totals count each call once:88 calls,69776 input tokens,37151 output tokens,1315.9976 summed request-seconds.46 calls hit length;42 stop. Token/latency unknown counts are zero. Monetary billing and separate cache-hit accounting are not recorded by this local HF instrument; no dollar/cache estimate is invented.

| Hypothetical pipeline, summed across8 coordinates | Calls | Input tokens | Output tokens | Summed request-seconds |
|---|---:|---:|---:|---:|
| Ordinary children+parent |32|35192|18649|659.5084|
| Same actual extraction+full parent |32|17136|7496|266.8569|
| Same actual extraction+lossy parent |32|13384|7496|266.5076|
| Direct256 |8|5560|2048|72.5393|
| Direct2560 |8|5560|6910|244.4945|

Full and lossy each receive the entire cost of their shared24 extraction calls. Summing these hypothetical rows double-counts those24 calls by design; it is not physical total compute. Ordinary children alone consume18243 output tokens/643.4437 seconds, versus extraction5448/193.9091. Ordinary parent prompt lengths3349–3714 are much longer than full1260 or lossy780–813. Thus report content, verbosity, parent prefill and child termination differ together. The expanded direct ceiling3×768+256 equals a maximum output allowance, not matched realized compute. All40 pipelines have physically retained constituents, but none of the ordinary/full/lossy/short pipelines has every constituent EOS-complete; all8 expanded-direct pipelines do.

## Ranked bounded followups

1. First calibrate final JSON formatting at a sufficient cap, not extraction width or training. A small clean paired screen is12 unique source inputs:all8 full-report coordinates plus4 deduplicated direct worlds, each with2560 cap under unchanged baseline interface versus a separately frozen JSON-only interface intervention (24 calls). Use fresh paired seeds, all four worlds, no selected failures, no gold in prompt, exact actual extraction reuse and fully charged hypothetical acquisition costs. A native grammar, if CPU-qualified, must constrain syntax/domain only, never encode the answer; otherwise a common stronger format instruction is explicitly a prompt-interface experiment. Keep cap equal across the new pair. Cap and format effects relative to this historical pilot are not separately identified by changing both at once. Freeze strict/native and diagnostic metrics plus a bounded wall cap before launch.
2. If the calibrated full-report parent has valid but wrong endpoints, test compact per-customer incidence/set presentation against raw triples with unchanged facts/visibility and a matched final interface. This targets state use/reduction, not missing child evidence. If direct also remains weak, revise task/interface difficulty before a communication claim.
3. Only after valid finals are demonstrated, restore ordinary/full paired comparison on all coordinates and replicate on fresh worlds. A wording/local-no-overlap emphasis ablation could test the observed anchoring hypothesis while keeping positive facts fixed. Do not make parents blind post hoc and call it the same experiment.

Do not rank blind more epochs, larger extraction caps (227/768 already exact), or a recursion/communication conclusion above this calibration. Existing ordinary facts are already sufficient in the manually audited cross cases, and direct strict ceiling is0 with mixed extractable semantic success.

## Artifacts and checks

Analysis directory:/project/alex_phd/runs/rlm-research-r4/analyses/root-partition-report-live-2026-09-09. AUDIT.json contains all88 call checks,40 endpoint rows, exact reports, costs and dependence. DIAGNOSTICS.json contains manual excerpts, set checks, pair tables and per-role costs. RAW_READOUT.md retains every call's output for inspection. OUTCOME_PINS.json binds raw sources; FINAL_MANIFEST.json binds the final additive analysis and this report. Original method files and all science outputs are preserved.

Six focused tests passed (four frozen primitives plus two no-repair/multiple-array diagnostics). CPU-only cached native reconstruction and annotation checks passed. The systematic-debugging skill kept the conclusion tied to observed component boundaries; no model/GPU/service/live queue or original-source changes were made.
