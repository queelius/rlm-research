# BROAD16: small, uneven transfer gain; no demonstrated broad generalization

Fixed final16 scores16/48 versus original13/48 on the prescribed transfer pairs:
eight gains, five losses and35 ties. All96 trajectories are observable and admitted;
there are no transfer nulls. This pooled+3 is descriptive across15 context groups,
not48 independent tasks or a new benchmark claim. The main64-record composition
comparison is unchanged overall at5/24→5/24. The net gain comes from the
leaf-test-exposed32 subset and the128-record subset;256-record tasks remain0/4.

| Prespecified stratum | Contexts | Original→final16 | Gains/losses/ties |
|---|---:|---:|---:|
| Composition64, trained targets | 6 | 2/12→3/12 | 3/2/7 |
| Composition64, reserved DESC/ABBR | same6 | 3/12→2/12 | 0/1/11 |
| Length128 | 4 | 2/8→3/8 | 2/1/5 |
| Length256 | 2 | 0/4→0/4 | 0/0/4 |
| Leaf-test-exposed32 | 3 | 6/12→8/12 | 3/1/8 |

Reserved DESC is0/6→0/6; ABBR3/6→2/6. These are known classes, not novel labels.
The same six composition contexts carry trained and reserved queries. They show
HUM gains in contexts02/04, balanced by NUM and ABBR losses in context05—not a
uniform improvement in reusable aggregation. Exact question/context bytes, seed,
source group, repeat and phase-specific episode IDs were reconciled through frozen
pair_id; actual task hashes and prompt hashes match within all48 pairs.

Context-level successes below keep repeats and requested targets nested. Full
hashes, pair vectors and trained/reserved within-context summaries are in METRICS.

| Frozen context suffix | Paired coordinates | Original→final16 |
|---|---:|---:|
| composition-064-00 | 4 | 0→0 |
| composition-064-01 | 4 | 1→1 |
| composition-064-02 | 4 | 0→2 |
| composition-064-03 | 4 | 0→0 |
| composition-064-04 | 4 | 0→1 |
| composition-064-05 | 4 | 4→1 |
| size-128-00 / 01 / 02 / 03 | 2 each | 0→1 / 2→1 / 0→1 / 0→0 |
| size-256-00 / 01 | 2 each | 0→0 / 0→0 |
| leaf-test-exposed-032-00 / 01 / 02 | 4 each | 3→2 / 2→4 / 1→2 |

## Learning execution and preserved missingness

All16 original-start updates are independently audited through the sealed
incremental chain, including exact1→…→8→9→…→16 Adam/adapter/RNG/input continuity,
finite nonzero tensor deltas, physical native action IDs/logprobs and root-only
masks. Across384 training attempts,379 are admitted;253 mixed-group episodes supply
540 root turns and171,288 action tokens. The126 admitted homogeneous episodes do
not enter updates. Child and observation loss tokens are zero; all correction
guards pass. The fixed child remainsc32de129…; final root isfa23ebc2… with checkpoint
statefd51f81d…. Neither successful optimization nor a correct count verifies all
child labels, evidence coverage or actual consumption.

Validation is5,4,9,8,8 successes/16 at steps0,4,8,12,16. Earliest maximum8 is
authenticated as descriptive only; transfer uses fixed16. Final validation has
6/8 successes at32 records and2/8 at64. There is no intermediate-checkpoint
substitution, reroll or transfer-based selection.

The combined lineage records all560 planned episodes:554 admitted, six excluded.
Four original STOP-era episodes have observable raw zeros but unadmitted graphs
with deterministic unsampled child errors; two later training episodes have no
observable terminal (round6 kernel/broker setup failure; round9 lxml installation
timeout). The original zero-update STOP is preserved separately; its24 saved
training attempts were reused for update1, not sampled again. No excluded zero
becomes an admitted negative. Detailed null paths/hashes are in
`METRICS.json:lineage.null_evidence`; installer traceback/source-command limits
remain in the sealed STEP12 evidence.

## Cost and operations

| Transfer cost,48 episodes per weight | Original | Final16 |
|---|---:|---:|
| Physical calls, root + child | 98+340 | 125+659 |
| Logical input tokens | 501,308 | 775,946 |
| Cached / uncached input | 449,600 / 51,708 | 730,640 / 45,306 |
| Completion tokens | 83,905 | 72,437 |
| Collection wall seconds | 418.80 | 416.85 |
| Valid final schemas | 31/48 | 38/48 |
| Length-finished calls | 21 | 7 |

More calls do not imply more cost in every dimension: final16 uses almost twice
as many child calls but fewer child completion tokens (52,642→11,921), while root
completion tokens increase31,263→60,516. No call-level truncation retrospectively
censors an earlier completed episode. These are descriptions, not a verified
mechanism or proof that longer output caps would improve accuracy.

All stages together made6,540 physical attempts:1,248 returned root calls,
5,281 returned child calls and11 errored child attempts; request-only remnants0.
Known logical input8,065,812 (cached7,606,672; uncached459,140), completion686,606;
usage is unknown on the11 errored attempts and is not imputed to zero. Requested
prompt IDs are retained for all6,540 attempts (8,166,204 tokens total).

Collection wall totals5,808.93s across the original and continued stages;
all16 optimizer/checkpoint steps430.46s. Continuation service startup-to-ready
totals761.13s across18 services; those clocks are not added to overlapping service
residence windows. Accepted continuation child elapsed6,915.38s; scientific run
6,912.54s plus original STOP1,170.54s gives8,083.08s combined scientific elapsed.
Child exit0/no timeout, FINAL/SELECTION/checkpoint markers and all18 owned-worker
release records authenticate. Last release→accepted-exit tail is at most0.513s,
not model compute. This independent audit held no GPU or scheduling lock.

## Audit limits and decision

The frozen method and new phase-aware pairing tests preceded transfer scoring.
The first pass verified both native/physical graphs and exact endpoints, then
the historical merge failed on a legitimately null schema-validity field. The
additive recovery preserves that source/error, counts schema unknowns explicitly,
and uses both pinned saved projections without rescoring any graph. It rehashes
their new source bytes once to recover the lost input receipt; old raw graphs and
optimizer tensors stay unopened. Eleven focused tests pass; the recovery completes
in4.05 CPU seconds. Its83 metadata/merge assertions are not presented as a rerun of
the first pass's graph checks. FINAL_NULLABLE_AMENDMENT documents the exact seam.

This does not support promoting broader16-step training as a general aggregation
solution. Retain it as uneven exploratory evidence; the smallest useful next
diagnostic is the already queued child-role/interface comparison, asking whether
costly child behavior and return consumption can improve without changing root
credit or silently excluding failures. Do not infer a breadth-only effect versus
earlier campaigns, whose update count, data and rollout volume also differ.

Evidence: METRICS.json and SOURCES.json; FINAL_RAW_PUBLISHED.json; stage seals
STEP1/4/8/12/16_PUBLISHED.json; scientific FINAL
`7cd76930b65cc674d1d9926fc91a381e87c1dcaeabb42e5c213e64ad6f1a1066`,
SELECTION `f9a757f243500cd85d71164898351f7de9ed9f521de1b393d7bafa3806dc8a9a`.
