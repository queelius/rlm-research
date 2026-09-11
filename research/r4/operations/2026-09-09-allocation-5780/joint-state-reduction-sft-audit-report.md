# Independent audit: joint-state reduction SFT

Audit cutoff: 2026-09-09 22:19 UTC. The 84-coordinate run is terminal and released. This
audit's method was frozen after launch and after capture, gate, and joint training had already
finished, but before this auditor read any readout scores. It is therefore an independent
post-launch audit, not a prospective preregistration.

## Answer

Joint training produced a large exploratory task-score improvement on free held-out rollouts, but
did **not** produce a corresponding increase in the narrow mechanism that motivated the run.
On the conservative frozen denominator, strict correctness was 8/16 for joint, 6/16 for
reduction-stop, and 2/16 for unchanged. The strongest joint result was on union queries (7/8,
versus 4/8 and 0/8). Yet only one successful free row in each policy executed a scalar reduction
from a live returned mapping before a strict stop. Joint often used another real strategy: it
copied authentic returned labels or IDs into a literal expression, or inspected a returned map and
then answered manually. Those are valid task successes, but they are not persistent live-state
accumulation.

The controlled continuation test points the other way mechanistically. With the same acquired
state replayed into all three policies, reduction-stop completed live-variable, user-scoped scalar
reduction and a strict correct stop on 4/8 rows, joint on 2/8, and unchanged on 0/8. Thus the result
supports “joint SFT changed useful policy behavior” more than “joint SFT learned the intended
acquire, accumulate, reduce, stop program.” It is exploratory evidence over four previously
research-exposed context clusters, not an independent replication.

## Strict outcomes

| readout | joint | reduction-stop | unchanged |
|---|---:|---:|---:|
| free held-out, lower-bound strict correct / 16 planned | 8/16 | 6/16 | 2/16 |
| free available | 12 | 14 | 15 |
| free strict-format responses | 10 | 11 | 7 |
| controlled held-out strict correct / 8 | 4/8 | 4/8 | 2/8 |
| training diagnostics strict correct / 4 | 2/4 | 2/4 | 0/4 |

Free uncertainty is explicit. Joint has three recorded operational NULLs
(`free-4103…`, `free-a076…`, `free-f5ba…`) and one unrun/missing result (`free-8b6a…`),
so its correctness bound is 8--12/16. Reduction-stop has one recorded NULL (`free-de90…`) and
one unrun/missing result (`free-a076…`), giving 6--8/16. Unchanged has one recorded NULL
(`free-0ff8…`), giving 2--3/16. Returned malformed or wrong responses remain observed zeros;
missing and operational failure are not rewritten as model errors.

Among coordinates where both policies returned outcomes, free joint versus unchanged had 7 wins,
1 loss, and 3 ties, with 5 unresolved pairs. Reduction-stop versus unchanged had 5 wins, 1 loss,
and 7 ties, with 3 unresolved. Joint versus reduction-stop had 4 wins, 0 losses, and 7 ties among
11 mutually observed pairs; five pairs were unresolved. If unresolved cells are mechanically
treated as lower-bound failures, the corresponding 16-slot counts are 8/2/6, 5/1/10, and
4/2/10; those latter loss counts are not evidence from paired observed outcomes.

The context-cluster free scores (correct/4; available in parentheses) were:

| context | joint | reduction-stop | unchanged |
|---|---:|---:|---:|
| new-root-train-00 | 3 (4) | 0 (4) | 0 (3) |
| new-root-train-01 | 1 (2) | 2 (4) | 1 (4) |
| new-root-validation-00 | 2 (3) | 1 (3) | 1 (4) |
| new-root-validation-01 | 2 (3; one unrun) | 3 (3) | 0 (4) |

The gain is therefore not uniform across four independent contexts. Repeated seeds within a
context are paired robustness checks, not extra independent context clusters.

## What the policies actually did

Every strict free success was preceded by an authentic, relevant child map, but trace evidence has
different strengths:

| successful free data-flow tier | joint | reduction-stop | unchanged |
|---|---:|---:|---:|
| scalar computed from a live mapping, then strict stop | 1 | 1 | 1 |
| live mapping filtered to a non-scalar result, then manually counted | 1 | 0 | 0 |
| authentic returned state copied into a literal reduction | 4 | 0 | 0 |
| relevant returned map observed, then manual answer | 2 | 5 | 1 |

The literal tier was checked against the preceding actual child response; it is not host-gold
leakage. It may be a genuine, if brittle and costly, learned strategy. Temporal provenance alone
does not prove causal dependence because the public records themselves were visible. The narrower
live-variable metric avoids making that claim.

The hoped-for persistent accumulation pattern was uncommon in free mode. Joint frequently sent a
single already-filtered batch, and its lone successful single-user row first requested four
disjoint batches but then reacquired the target subset rather than combining those maps. Three
joint rows repeated acquisitions until 91--93 actual sampled requests without a final. A contrary
example acquired a relevant map, ignored it, searched question text for the phrase `human being`,
and returned the wrong zero.

Controlled traces isolate the correction step more sharply. Joint achieved live, scoped scalar
reduction on 2/8; reduction-stop achieved it on all four of its strict successes (4/8); unchanged
made no tool call and achieved 2/8 by direct stopping. Joint also counted an entire accumulated map
instead of the requested `u03` subset on one row (observed 2, gold 1), and another correct row
overwrote category values with user IDs before stopping. Several width-16 trained-policy rows
reacquired labels or reset the supplied accumulator. Width-4 live-scalar success was joint 2/4,
reduction-stop 3/4, unchanged 0/4; width-16 was 0/4, 1/4, and 0/4 respectively. Width is confounded
with the variable alias in this pilot, so this is not a clean length effect.

Training diagnostics are exposure checks, not held-out generalization: joint and reduction-stop
each scored 2/4, unchanged 0/4, on four states drawn from the training corpus.

## Training and native evidence

The 16 teacher trajectories used disjoint source groups from the 64 raw evaluation groups. The
evaluation compositions are held out from training, but their four contexts had appeared in prior
research. Training variables were balanced across four aliases; widths and single/union families
were each 8/8. Host gold was not present in model-visible artifacts. All 40 teacher child calls and
20 controlled-source child calls were actual returned `c32` requests with pinned corpus and map
checks. Replayed controlled/diagnostic acquisitions were byte-identical and were not charged as new
calls.

The fixed gate passed before optimization: four audited mechanism spans had NLL above 0.1 and no
gradient or optimizer step occurred in the gate. Independent checkpoint loading found exactly four
Adam steps in every checkpoint of both arms, finite optimizer state, and fresh optimizers. The
fixed checkpoint-4 adapter hashes were `ffa49801…fd00` (joint) and `eaa80a9f…c81ac`
(reduction-stop).

The arms were not compute matched. Joint used 20,064 target-token exposures, 452,384 forward-token
exposures, and 288 root-turn exposures; reduction-stop used 5,024, 225,520, and 128. Optimizer-loop
elapsed time was 182.57 s versus 93.73 s. Full training-stage time, including setup/checkpointing,
was 197.75 s versus 110.94 s. Joint's weighted training loss fell from 0.940 to 0.387 and
reduction-stop's from 1.359 to 0.434, but loss decline is not the research endpoint and does not
resolve the unequal-token/FLOP confound.

Native authentication covered all 82 materialized results: policy alias and adapter hash, exact
wire request/response match, preserved prompt and completion token IDs, trace linkage, final branch,
finish status, and independent strict rescoring. All 77 available finals passed the full final-branch
check; the five recorded unavailable results had no authenticated final and remained NULL. Runtime
scores agreed with independent scores on all 82 results. The two planned but unrun free coordinates
remain separate missing inventory entries.

Physical source acquisition was 40 actual child requests for training (36,996 exact input and
2,460 exact output tokens) and 20 for controlled held-out states (18,670 input and 1,218 output
tokens); cache-hit token accounting was unavailable. Free readouts made 401, 281, and 77 new actual
sampled model requests for joint, reduction-stop, and unchanged respectively. These are local model
requests and token counts, not provider billing. Hypothetical standalone replay costs are retained
in native results but were not physically incurred three times.

## Interpretation and next comparison

The decision-relevant signal is real enough to follow up, but the mechanism claim should be
narrowed. Joint SFT improved strict free task completion, especially for union queries, while also
increasing looping and request cost. It did not beat reduction-stop on the cleanest supplied-state
reduction diagnostic, and neither trained arm improved the one observed live-scalar free success
over unchanged.

Ranked next tests:

1. Replicate the 16 free coordinates on genuinely new context clusters with a fixed request cap and
   retain the three state-use tiers. This tests whether the union gain survives without turning
   repeated seeds into independent evidence.
2. Run a clean accumulator intervention: identical acquired maps, orthogonally randomized alias and
   width, with the map either kept live, replaced by an equivalent literal, or removed. This
   distinguishes learned live-state use from copying/reading the observation.
3. If training continues, equalize total target tokens and forward tokens between joint and
   reduction-stop. Retire the joint objective if it does not improve live-variable reduction or
   request efficiency under that comparison.

## Audit artifacts

The authoritative machine-readable evidence is in
`analyses/root-joint-state-reduction-sft-live-2026-09-09/`: `METHOD_READY.json`,
`TRAINING_AUDIT.json`, `OPTIMIZER_AUDIT.json`, `SOURCE_COST_AUDIT.json`,
`READOUT_AUDIT.json`, and `MECHANISM_AUDIT.json`, with their corresponding audit programs.
`FINAL_MANIFEST.json` seals the report, method, audit sources, and result artifacts.
