# Checkpoint4: valid training updates, no validation improvement yet

Validation4 is **4/16 strict-correct versus original validation0's5/16**. All16 new
episodes are observable and graph-valid, with no failed physical requests or
budget censoring. The raw paired comparison is two gains, three losses and11 ties.
Among the15 pairs with valid graphs on both sides, the scores are still5 versus4.
Thus infrastructure exclusions do not explain the current validation errors.
This small exposed developmental comparison does not establish a general negative
learning effect, and it does not change the prescribed fixed-final16 primary.

All three new optimizer increments pass independent checks: actual Adam cursors
are2,3,4, the preceding adapter/optimizer/RNG identities form an exact chain, and
each consecutive adapter change is finite, nonzero and agrees with the saved
training metric. The child remains fixedc32de129… and receives no training credit.

## New episode and update denominators

| Stage | Raw strict correct / attempted | Observable / graph-valid | Terminal-schema-valid | Selected update rows | Collection wall seconds |
| --- | --- | --- | --- | --- | --- |
| Round2 |7/24|24/24;24/24|15/24|24|181.627|
| Round3 |5/24|24/24;24/24|21/24|16|215.700|
| Round4 |15/24|24/24;24/24|21/24|24|184.285|
| Validation4 |4/16|16/16;16/16|15/16|Not training|200.534|

All88 new episodes were present, independently rescored from raw terminal replies,
and matched their frozen coordinate/task/context/seed and saved exports. There are
zero null raw rewards, zero infrastructure exclusions and zero budget-censored
episodes in this delta. Observed malformed terminal answers remain wrong, not
missing: validation4 has11 schema-valid wrong answers and one schema-invalid wrong
answer. Graph validity is not a claim of answer correctness.

Round3's16-record entity group is eight valid observed wrongs with all-zero reward.
Those eight rows are retained in the export but do not contribute a mixed-reward
gradient. The other eight new task groups are mixed and contribute all their rows.
Round2's three groups have2/8,4/8,1/8 successes; round3 has0/8,4/8,1/8;
round4 has3/8,6/8,6/8. Different rounds use different frozen tasks and contexts,
so the rising round4 training score is not a matched learning curve.

Including reused round1, four updates have consumed79 selected episodes from96
attempted training episodes:93 graph-valid,14 valid all-zero-group rows unselected,
and the original three infrastructure-excluded rows still excluded. This does not
reclassify the original STOP or count its24 training episodes as newly collected.

## Actual optimizer, masks and correction

| Actual Adam step | Root turns / action tokens | Consecutive adapter L2 change | Training with checkpoint seconds |
| --- | --- | --- | --- |
|2|50 /15,699|0.13820451024974015|40.848|
|3|36 /10,500|0.12341438942851433|28.512|
|4|49 /11,496|0.11333605497789682|34.309|

Each CPU-loaded Adam state contains all504 parameter states at the expected cursor,
with finite tensors and unchanged learning rate0.00005/weight decay0. Parameter
name order is identical across checkpoints1–4. The captured adapter-load audits
name each exact preceding adapter and confirm exact loaded values and dtypes.
Checkpoint state authenticates complete INPUTS and correction-capture bytes;
each native preflight receipt names the pinned new verifier, replays24 records and
selects exactly the independently identified mixed rows. None reports a recovered
checkpoint or a reapplied update.

All135 newly trained root turns and37,695 current action tokens match their actual
physical native request/result token IDs and behavior logprobs. Each prior causal
prefix is masked; only the current root action suffix has credit. Child and
observation loss tokens are zero. Capture arrays form an exact bijection with
selected turns; their lengths, source IDs, advantages and equal-episode/then-turn
weights agree. Every native-to-proximal ratio and cap2 correction was checked.

All five guard statistics were independently recomputed from saved capture arrays.
Across updates2/3/4, mean absolute log-ratio is0.007220/0.005369/0.006641 and raw-token
ESS fraction0.997151/0.997173/0.997539. Sample-k3, out-of-[0.5,2] fraction and removed
importance mass also match their saved values and pass every frozen bound. These
are likelihood-distribution checks, not child semantic validation.

## Matched validation trajectory by context/task

Each row has two fixed seeds. The same task/context/seed coordinates are compared;
the original graph-invalid episode remains a separate limitation of that arm.

| Validation context and target | Original successes | Checkpoint4 successes |
| --- | --- | --- |
|32-record00 HUM|0/2|0/2|
|32-record01 NUM|0/2|0/2|
|32-record02 ENTY|1/2|1/2|
|32-record03 LOC|0/2|1/2|
|64-record00 HUM|2/2|1/2|
|64-record01 NUM|1/2|0/2|
|64-record02 ENTY|0/2|0/2|
|64-record03 LOC|1/2|1/2|

The current evidence supports “training is executing, but validation has not
improved at step4,” not “broader RLVR is effective,” nor a decision to select another
checkpoint. Context count is small and these are exposed developmental coordinates.
Full fixed-final16 transfer is still pending.

## Cost and provenance

The four new collections made792 actual physical requests:189 root and603 child,
all returned. Native wire usage reconstructs802,948 logical prompt tokens,
744,864 cached,58,084 uncached, and76,329 completion tokens (50,739 root;
25,590 child), with no unknown usage entries. Returned native IDs, logprobs,
request/result identity, sampler and physical adapter bindings were checked, not
merely aggregate exporter scores.

Measured collection wall time totals782.146s, and updates2–4 including checkpoint
saving total103.669s:885.815s of reported stage work. This is not the entire campaign
elapsed cost: service startup, native preflight, coordination and other overhead
are outside those particular timers. Overlapping request durations were not summed
as GPU wall time. Original1170.540s STOP work and update1 remain in their earlier
snapshots. The unchanged new-work cap is16,829.460386276245s, inclusive cleanup
16,949.460386276245s, outer16,980s; actual campaign-total accounting awaits terminal.

The88 new raw graphs were reconstructed once using the pinned prior independent
audit (`141579957d56fdc04fe5cb7033d5f408ee232af4985290032e165fddeb923886`), with exactly
two count-checked source substitutions replacing its original-only policy assertions
with each stage's exact expected checkpoint. No scoring, masking, graph or admission
rules changed. The old40 raw graphs were not reread. The main projection and
checkpoint checks completed91,332 assertions in11.306s of execution, followed by
small saved-capture guard and array checks. Five focused tests pass, including the
three existing root-mask tests and two new log-prefix tests.

One audit-only publication issue occurred after all scientific checks and STEP4.json
were written: the generic immutable source cache rejected append growth in the
still-live checkpoint4 service log. Its captured old prefix was subsequently
authenticated by hash without reading the3,579 newly appended bytes. All four service
log prefixes verify;1,700 other raw-cache files retain exact stat identity. A bounded
recovery pass rehashed33 checkpoint provenance files once; it did not rescore any
episode or reload any optimizer/adapter tensor. The original failure is recorded in
STEP4_SOURCES.json, alongside the final recovered provenance. Thus the projection is
not falsely presented as a clean exit0 run. Scientific artifacts were unchanged.

Machine-readable evidence: STEP4.json; per-stage STEP4_*_RAW.json; updates
STEP4_UPDATE_02/03/04.json; STEP4_GUARDS.json; STEP4_SOURCES.json. Step1 remains sealed.
No GPU/model call, service action, process query/signal, acceptance, source change,
or later-than-checkpoint4 outcome inspection was performed. Await the next parent
milestone trigger; do not substitute checkpoint4 for fixed-final16.
