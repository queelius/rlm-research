# BROAD16 continuation: checkpoint1 is a real, correctly bound update

The continuation has executed one new AdamW update from the original root using
the saved first-round data. This is not an update replay and not a new independent
training seed. The checkpoint passes the bounded independent execution audit;
there is no performance or transfer conclusion yet. Fixed-final16 remains primary.
No round2-or-later outcome contents were inspected.

## What was verified

| Check | Independently checked result |
| --- | --- |
| Saved training coordinates | Same24 episode IDs, task IDs, seeds, raw endpoint rewards and graph-admission status as the sealed original STOP audit |
| Actual first-update rows | Exactly15: seven16-record HUM rows and eight32-record NUM rows; six admitted all-zero64-record ENTY rows do not enter mixed-group training |
| Exclusions | All three previously unadmitted rows remain excluded; none is repaired, resampled, newly admitted or given a manufactured reward |
| Actual credited actions | 25 depth0 turns;8,141 current root-action tokens; every prefix label is−100 and mask0; every current action label equals its sampled token ID and mask1 |
| Native correction | Every captured rollout logprob equals its saved native value after the trainer's FP32 conversion; saved HF-minus-native ratios and cap2 correction weights independently recomputed for all8,141 tokens |
| Loss weighting | Population-standardized advantage within each admitted task group; equal episode, then equal root-turn weighting |
| Adam state | CPU-loaded optimizer contains all504 parameter states, every actual step cursor exactly1, finite tensors, learning rate0.00005 and weight decay0 |
| Root weights |504 matching finite adapter tensors;252 tensors changed; independently computed L2 change0.14765541457707412, matching saved0.1476554145770741 |
| Original start | Original root857a7ce6… at step0, no inherited optimizer/RNG/state checkpoint; frozen seed981268001; childc32de129… remains fixed and was not loaded into the training model |
| Saved validation0 | Symlink to the original16-episode validation0, not replayed; saved round1 generation hash is unchanged |

The504 tensors contain16,515,072 trainable parameters. A nonzero overall update
does not require every tensor to move in the first step. Saved optimizer/update
metrics report gradient norm0.18954149, no distribution-guard failures,
17.5248s optimization and18.3858s including checkpoint. Correction mean absolute
log-ratio0.0108166 and raw-token ESS fraction0.995879 pass the frozen guard bounds;
these establish distribution compatibility, not correctness of the answers.

## Narrow source delta and real training preflight

Frozen READY is `36a5e1c2cf8ce6f1a86bbc739ccdc275f4a098953f0dcac117fe3301f3b3f48b`.
AMENDMENT is `d570e4d099b535ad7c7b287285cd34f9c22f4526470d91899bf7e3f4431772ab`.
The inspected private native adapter first uses the original rejection verifier.
Only its specific unrecognized-error exception permits the new exact8192-token
child400 wording, requiring at least one further output token. Its count-checked
source replacement changes the old `len(ids) <= 8192` rejection test to
`len(ids) != 8192` in the separate equality verifier. The original greater-than8192
path remains intact. Other role, model, sampling, failed-response and unsampled-node
checks are retained. Root rejections are not admitted and no native graph is edited.

The training wrapper routes only the exact old native `verify-export --output`
subprocess to the pinned new verifier. The original trainer still performs its
remaining group/generation/recipe authentication. The actual training INPUTS receipt
records24 replayed exports,15 selected rows, the exact prepared GROUP/MANIFEST hashes,
and new verifier SHA `e8758845094509e1b739774c9b7d2062db13afac692012f6f9c943b04e129157`.
The receipt is bound by checkpoint state to the actual INPUTS bytes. This audit did
not rerun native replay or claim a second independent raw-graph verification.

The unchanged upstream trainer validates root turns, runs all forward/backward
passes before its single `optimizer.step()`, and saves actual Adam state afterward.
Its TIS loss selects only logits predicting the current action suffix. HF proximal
likelihood is `current.detach()` at this single full-batch update; the distinct
behavior likelihood comes from native rollout capture, not an alias mask or invented
logprob. The child's text may occur in masked causal context but is not a credited
child training sequence.

## Evidence and scope

The completed original audit and its publication hashes were authenticated first.
This pass reused1,977 prior file hashes only after exact device/inode/size/mtime/ctime
identity checks;96 additional artifacts were content-hashed. The closure cache is
in STEP1_SOURCES.json. Original40 native graphs were not reread. Prepared rows and
correction arrays were checked directly, while authenticity of their old native
request/result source inherits the sealed original audit. All25 trained turns are
bound to its original-root physical audit files and retained all-role evidence.

The initial audit attempt stopped before tensor reads because its code compared a
nested episode digest with a whole-record file hash. Source inspection established
the distinction; the assertion now compares `source_record_sha256` with the old
whole-record hash, matching all15 rows. This is an audit-code correction, not an
experiment correction. It caused a second lightweight closure pass; adapter and
optimizer tensors were each deserialized only once. Early metadata inspection also
printed oversized already-exposed prepared/prior summaries, and a source search
matched unrelated historical root-credit exports; neither was used as new evidence
or a reason to modify the method. No new continuation outcome beyond checkpoint1
was opened.

The successful pass completed21,242 assertions. Three focused synthetic tests pass:
valid root action suffix, rejection of child/context credit, and rejection of absent
or nonfinite native likelihood. These tests ran after the initial projection; the
projection itself provides full real-data assertions. Method freeze preceded new
checkpoint-content inspection and is recorded by METHOD_READY.json.

## Costs and remaining question

The original zero-update STOP remains a separate historical result:40 attempted
episodes and1,170.5396137237549s work. The continuation retains exactly
16 total updates, validation4/8/12/16, and fixed-final16 transfer. Its520 newly planned
episodes are360 training +64 validation +96 transfer; reused40 must not be counted
as newly collected. Remaining work allowance is16,829.460386276245s, so the combined
lineage's work cap stays18,000s. Inclusive continuation allowance is
16,949.460386276245s including120s cleanup; outer cap16,980s, also subject to the
earlier allocation deadline. These are caps, not actual elapsed continuation costs.

The next authorized audit is checkpoint4 after the parent's trigger. A successful
checkpoint1 proves the equality-boundary continuation can train on the retained
data; it does not yet show that broader RLVR improves the root, generalizes to new
contexts, or beats the original policy. Existing validation/test coordinates remain
exposed developmental data. No GPU/model call, process query/signal, environment
installation, runtime source edit, acceptance or launch was performed by this audit.

Checkpoint: `sidecars/root-broad-equality-continuation-v1/outputs/attempt-001/round-01/training/checkpoint-1`.
Adapter SHA `cb10423678447540568d5c6ad773ccfc3dcc1159cf90dd28398dcf177d18aa0f`;
Adam SHA `56e5accb3c8e8afbae374ab8e43c82b2f779ee3a97160a006093a38585858469`;
state SHA `2022537e002584ed5dc44a1092e525b55a0c3b36f8174cee1bdd5b2e390e2d64`.
Full machine-readable execution evidence and diagnostic values are in STEP1.json.
