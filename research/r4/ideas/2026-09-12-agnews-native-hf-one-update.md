# Proposed AG News batch-four native/HF one-update pilot

Status: CPU source review and design only; not implemented, accepted, or launched.

Question: can a single qualified importance-corrected helper update on new AG News
records, with training requests shaped like the heldout requests, improve the frozen
AG heldout256 readout? This is an exploratory package (domain, new data, request
granularity, count reward, and dose), not an isolated mechanism or RL superiority test.

## Small fixed experiment

Start original c32, not a previous RL checkpoint. Use exactly the existing128
`helper-agnews-data-vs-mechanics-v1/inputs/TRAIN_PUBLIC.json` records in its already
frozen label-blind presentation order, partitioned into32 consecutive groups of4.
No grouping by correctness, prediction, or host label; no heldout text in training.
Use the standard AG prompt builder and the existing helper chat prefix/suffix,
four actual labels and keyed ordered JSON schema. Gold remains host-only.

Collect four native completions per group:128 calls,512 scored record decisions,
128 unique training records. Native temperature0.5, top_p1/top_k-1, no penalties,
1024 completion cap, exact stop IDs151645/151643, processed chosen-token logprobs.
Temperature0.5 deliberately preserves the successfully qualified fast48 seam;
it is not a temperature search. Use one batch-invariant V4 native service, c32
binding only, concurrency4. Require the actual EngineCore marker, not just the
requested environment flag. Pin every request/body/schema/tokenizer hash and
unique provider request ID; checkpoint request/response and normalized record per
call. Preserve errors and missing actions; do not retry or train on a subset.

Prospective seed namespace `agnews-b4-native-hf-step1|20260912`; native seed
202609122100 + 4*group_index + repeat (0..3), with repeat-major fixed schedule.
HF Python/Torch/all-CUDA seed202609122300 and NumPy seed modulo2**32. No sample
selection. These seeds must be recorded before collection in the eventual READY.

Reward is fraction correct over4, with reward_scale4 in existing RLOO math: thus
the actual advantage is correct-count minus the mean correct-count of the other
three completions for that identical request. Preserve every all-zero/all-one or
equal-count group; it contributes zero, without renormalization. Record count
histograms, mixed-reward groups and category errors. New requests may create more
signal than nearly solved TREC singletons, but this is a hypothesis, not a guarantee.

## Existing narrow seams and exact gates

1. Builder: `helper-agnews-heldout-eval-v1/prepare_eval.py::make_inputs` shows the
   correct standard AG request replacement. Reuse that construction for TRAIN_PUBLIC,
   not its heldout input accessor. The frozen heldout REQUESTS must remain untouched.
2. Native wire: reuse V2 qualification collector's raw byte persistence, token-ID
   decoding, strict response/usage checks, and V4 service/release owner. Its old
   normalization hardcodes16 keys/reward denominator and48 calls/2x24 contexts;
   a small new normalizer must explicitly require4 keys/128 calls/32x4 groups.
   Do not fake compatibility by padding or leaving old inventory constants.
3. After native clean release, call sealed
   `root-qs6-leaf-rloo-onebatch-v1/prepare.py::generate_masks` in the native Python
   with CUDA hidden. The training Python lacks xgrammar: use the already successful
   precomputed-mask handoff, not another import/install attempt. Exact ordered schema,
   any_whitespace=True, stop IDs and every sampled token including EOS are checked.
4. Load HF c32 only once, after the native release receipt. Reuse sealed
   `_selected_logprobs`, `importance_diagnostics`, and `objective_term`; score all
  128 records in eval/dropout-off BF16 base/FP32 LoRA, SDPA/noKV, before creating an
   optimizer. Require finite supported actions, ESS >=102.4 (0.8*128), and maximum
   normalized importance weight <=0.1. Raw full-sequence ratios are detached,
   neither clipped nor self-normalized. Passing this gate does not prove arbitrary
   HF/vLLM identity or validate any old processed logprobs.
5. In the same loaded model, preserve the fast48 gradient path: train mode with
   every dropout module eval, nonreentrant gradient checkpointing and FP32 LoRA.
   Replay every trajectory through the same full teacher-forced forward, requiring
   token error<=1e-5 and sequence error<=1e-4 against the pre-step HF scores. One
   trajectory graph/backward at a time, no128-graph retention. Loss is
   `-sum_i(stopgrad(ratio_i)*advantage_i*sum_t(logp_i,t))/128` over completion tokens
   only. No prompt, root, environment or gold-answer token loss.
6. Only after all128 replay gates pass: fresh AdamW LR1e-5, weight_decay0, clip1,
   exactly one step. Require finite positive gradient and adapter delta, optimizer
   state step[1], then save adapter/config/optimizer/RNG/state, qualification,
   gradient replay, source lineage and full STEP_COMMIT/EVAL_BINDING. Gate failure,
   zero signal, invalid/missing action, context failure or deadline => NO_UPDATE;
   no relaxation, truncation change, fallback or hidden second batch.

The new thin owner can combine the two existing HF passes in one process/model
load. This is materially smaller than a new training framework: new input builder,
128-action normalizer/accounting, and a scoped owner assembling already reviewed
numeric functions. Estimated CPU implementation25–35 minutes, two focused fixtures
(real4-key native raw/gold/mask fixture; actual tiny-model qualification/backward
with one-step and failure/no-step), no installation or broad refactor. If the
native-to-HF handoff cannot be kept within that bound, stop and retain the existing
true-HF AG four-step candidate as conditional rather than creating infrastructure.

## Caps, evaluation and decision

Proposed training owner1100/external1200 seconds: native650, native-CPU mask handoff
60, HF350, plus40 cleanup reserve. All phase caps are inside one owner deadline.
Expected5–12 minutes is a prospective estimate;128 new longer AG prompts have not
been timed. Before seal, record min/max prompt lengths and prove prompt+1024 fits
the unchanged real service context cap. No prompt shortening after seeing results.
Native service must fully release before HF; HF must exit before native evaluation.

Conditional updated readout reuses the exact64 batch-four temperature-zero request
bodies/seeds in `helper-agnews-heldout-eval-v1/inputs/REQUESTS.json`, matched to c32
on those same256 records. Use the existing V2 native evaluator's exact runtime for
both arms. Existing c32 source reuse requires full matching runtime/config/raw
qualification; otherwise collect a fresh c32 arm. Report service history/cost
separately if baseline is reused. Each native arm retains600 owner/700 external.
Primary: correct/256 and paired wins/losses, with per-class confusion and fixed
missingness denominator. Training behavior reward is not heldout accuracy.

Promote only to a fresh-seed replication if a fully qualified update completes,
the complete matched readout has positive net paired wins, and cost is plausibly
competitive. One-record movement is not evidence of an established gain. If zero
signal or an importance/replay failure occurs, it directly informs the next choice
without silently changing this pilot. Do not choose checkpoint, records or a
four-step continuation using heldout examples. Four steps would require a separate
prospective decision and fresh on-policy native collection after each step.

Dataset source is fancyzhx/ag_news train revision
`eb185aade064a813bc0b7f42de02595523103ca4`; selection manifest excludes verified c32
5065, current32, old256, fresh-adaptive128 and known root IDs/normalized text. Train
and heldout normalized-text overlap is zero. This is heldout from verified helper
optimization, not a claim about base pretraining. License was unspecified in the
pinned card; local research only, no inferred redistribution grant. The heldout
panel is research-exposed once current reference readouts are inspected.

Source review pins:

- Data MANIFEST SHA `dd50933ba660e056777f1b29cfdb32348cd4f2fe31975550dcfbc1b8bcc59a73`.
- TRAIN_PUBLIC SHA `2c2ad96833e8d870625faad3066a6b2b1d654b298232a27b86a6e510385d44d2`.
- TRAIN_GOLD SHA `3eb29c82c4535c6a91128c54549119c863848a82b7b27be9949e9ed7d89b30f4`.
- Heldout REQUESTS SHA `28c4b9aa984b9aa2afb796b288ee338f576ae0d04c6f8de12cd3af7f70e3f549`.
- C32 readout READY_V2 SHA `0233757687489e9adcd7c8cb0c8548abadba212ef3ba1a2528655e9884596768`.
- Fast48 update READY SHA `c4a631fae66b535cdf681f45c41454bce5c6086e0ba0eee076e144d236350509`;
  completed RESULT SHA `990431f25012059f619cbba98416c15b8eaf30cc54d3f23a999098fd978c4f5b`.

Proposed new sidecar: `helper-agnews-native-hf-onestep-v1`; no directory/code created
by this proposal. All listed sources remain sealed and unchanged.
