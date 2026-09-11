---
schema_version: "rlm-question-card-v1"
id: "rq:reduction"
title: "Can explicit reduction of actual supplied maps improve end-to-end answers without gold or automatic submission?"
status: "followup_design_priority"
updated_utc: "2026-09-10T03:29:00Z"
evidence_cutoff: "2026-09-09T17:32:51.282711+00:00"
living_update_cutoff_utc: "2026-09-10T03:29:00Z"
source_catalog:
  path: "/project/alex_phd/runs/rlm-research-r4/analyses/research-factory-2026-09-09/CATALOG.json"
  sha256: "e0fa23412505eee178d27041816e84f7931d6da01b02e13f664393a6586ff39c"
related_questions:
  - "rq:controller"
claim_ids:
  - "claim:reduction-not-restatement"
  - "claim:coverage-relative"
  - "claim:bridge-no-task-gain"
reports:
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-canonical-source-loader-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-canonical-source-loader-live-2026-09-10/REPORT_CORRECTION.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-semantic-map-externalization-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-fresh-join-externalization-order-live-2026-09-10/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-query-failure-taxonomy-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-coverage-first-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-child-representation-bridge-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-supplied-map-reducer-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/visibility-audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-map-contract-clarity-live-2026-09-09/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/corrective-sft-audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/analyses/root-corrective-reduction-sft-live-2026-09-09/completion/REPORT.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/artifact-restart-audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/state-content-factorial-audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/state-content-factorial-audit-report-erratum.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/joint-state-reduction-sft-audit-report.md"
  - "/project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-allocation-5780/joint-state-reduction-sft-audit-report-erratum.md"
publication_readiness: "not_publication_ready"
---

# Can roots reliably reduce supplied maps?

## Latest sealed evidence and revised question at03:29 UTC

The semantic-map externalization comparison separates reading, faithful use and
final accuracy. File-only maps increase actual reads7→19/24, but faithful map
reductions only9→11/24 and correct answers5→7/24. Nine of20 faithful reductions
are wrong against the dataset because the acquired labels are wrong. All eight
missing finals arise from malformed model-generated tool calls; they are not
random transport dropouts. File-only also uses71 root calls versus34, so this is
not a general efficiency improvement. Eight exposed source contexts limit scope.
[Independent semantic-map audit](../analyses/root-semantic-map-externalization-live-2026-09-10/REPORT.md).

On fresh generated factual worlds, file-only evidence produces16/16 real loads,
16/16 native finals and12 correct, versus no file loads,10/16 finals and9 correct
with inline facts. Complete pairs do not show file-only accuracy superiority.
Some file-only errors follow successful loading: after a NameError the root
replaces genuine evidence with invented records. Other errors use order-sensitive
set accumulation. This directly motivates a voluntary canonical-data loader, not
an automatic correct answer or host-supplied reduction algorithm.
[Independent fresh-world audit](../analyses/root-fresh-join-externalization-order-live-2026-09-10/REPORT.md).

The canonical-loader48 has finished with the same eight historical maps and
fixed policies. FILE7/24 planned and22 native finals compares with LOADER10/24 and
21 native finals. Yet actual loader use is1/24, reloads0, and all21 faithful map
reductions use ordinary files. Four faithful calculations inherit wrong source
labels; five native NULLs are model-generated tool/context failures. The corrected
context tally is4 loader wins,1 file win,3 ties, not the original5/1/2 prose.
[Independent audit](../analyses/root-canonical-source-loader-live-2026-09-10/REPORT.md),
[correction](../analyses/root-canonical-source-loader-live-2026-09-10/REPORT_CORRECTION.md).

Do not attribute the answer difference to canonical restoration when that behavior
was absent. The intervention bundles module availability and its description;
the next useful question concerns adoption and correct use, not another unused
helper. Published-controller reachability and teacher-first versus free initiation
are queued/being prepared. Generic external memory/state is prior art.
[Methods-informed context](../ideas/2026-09-10-format-binding-state-literature.md).

## Question

Can a root explicitly reduce an actual supplied label map into the correct strict native answer
without gold repair, host-computed substitution, or automatic submission?

## Why it matters

This test separates child semantic quality from the root's ability to preserve scope, interpret the
container, execute the requested reduction, and emit the computed result. It targets an observed
bottleneck more directly than teaching answer restatement.

## Evidence so far

At the catalog cutoff, `claim:query-diagnosis` supports `claim:reduction-not-restatement`: in 32
reused query trajectories, every one of 19 displayed integer scalars was copied faithfully, while
six cases had a correct map without an executed count. See `exp:taxonomy32` in the sealed [failure
taxonomy](../analyses/root-query-failure-taxonomy-2026-09-09/REPORT.md).

`claim:coverage-relative` reports that withholding partial ledger counts beat always showing them by
3/8 and 2/8 for two roots, but beat unchanged map-only by only 1/8 and 0/8. See `exp:coverage48` in
the sealed [coverage study](../analyses/root-coverage-first-live-2026-09-09/REPORT.md). Contrary
evidence from `claim:bridge-no-task-gain` shows that better count-label agreement did not improve
count or checksum endpoints in `exp:bridge32`; see the sealed [bridge
report](../analyses/root-child-representation-bridge-live-2026-09-09/REPORT.md).

### Later sealed update outside the catalog cutoff

The [three-root bridge audit](../operations/2026-09-09-allocation-5780/audit-report.md) keeps checksum
at 0/8 in every root/representation cell. Its focused traces expose the combining bottleneck: one
root treats a returned dictionary as an iterable of labels and zips its keys into new values;
another visibly receives a complete map implying 7 but emits 13 without displaying a computed
scalar. RL4's two map count gains come with changed syntax or batching, so they do not isolate map
representation. This later evidence favors a supplied-map/reducer diagnostic while showing that a
generic map intervention is not robust across roots.

### Completed update after the original question-page snapshot

The [supplied-map audit](../analyses/root-supplied-map-reducer-live-2026-09-09/REPORT.md)
is sealed (report SHA256 `df074ae652f62d3cf32198a47636bd3bb323baf7992227d015ffdbffcf9aec40`;
final SHA256 `b9be310b98f7dd68787c2aaacc4dda4c02f8c9aa8c24ebc9266cbd850b49a884`).
Ordinary Python scored 5/8 with actual child maps and 5/8 with explicitly
privileged dataset maps; making the counting helper available scored 3/8 and
2/8. All 32 native finals were available. Only one of 16 helper endpoints
actually invoked the helper, and its successful call used a newly requested
child map. No successful helper reduction used the supplied map. This test
therefore does not isolate arithmetic ability or the benefit of correct labels.
It prioritizes checking whether prompt examples and evidence placement affect
use of supplied information before scaling the reducer comparison.

The resulting [visibility audit](../operations/2026-09-09-allocation-5780/visibility-audit-report.md)
is sealed through the living cutoff (report SHA256
`7ba22267b0efc4d61343ebb3278bc2420d258d9f674c88e35ce00e38d4bb310b`; final-manifest SHA256
`dcf920b53994781bbfcb128d300b0ecbe4338e89999546e6544654c1160ddd94`). Strict dataset
correctness is 24/32 and exactly 6/8 in every example×visibility cell, across eight query blocks
nested in four context clusters. Manual code/trace audit supports actual supplied-map state use in
26/32 endpoints: 25 programmatic reductions and one file display followed by a prose reduction.
The other six—all example-present/file-only—make a child call and overwrite the supplied map.
Every inline endpoint still opens `labels.json`; no executed code parses the inline payload. Thus
the zero correctness contrasts do not prove treatment equivalence or a causal inline-visibility
benefit, but they do expose example-conditioned reclassification.

The later [field × map-contract audit](../analyses/root-map-contract-clarity-live-2026-09-09/REPORT.md)
is sealed (REPORTad8f2d93…, SEAL3d3f40eb…). Correct counts are14/10/17/17 across
F0M0/F0M1/F1M0/F1M1, with23/24/24/24 available. Accurate actual fields eliminate
all18 observed field-error endpoints. Map wording is a bundle, not an isolated
permission or filename effect, and does not consistently increase map uptake.
Although48 endpoints load the map, only18 use it for a scoped scalar or list.
F1M1 has23/24 map-consistent answers but only3 supplied-map scalar reductions;
17 reductions instead use new child labels. Agreement cannot substitute for
executed data-flow evidence. Four source contexts and three paired seeds per query
do not constitute96 independent tasks. One unreturned Jupyter endpoint stays NULL.

### Corrective training and restart update at21:41 UTC

The [original corrective training audit](../operations/2026-09-09-allocation-5780/corrective-sft-audit-report.md)
does not establish free-root improvement: unchanged10/32, producer-only2/32,
corrective7/32 planned (25 available). Both four-update arms completed, but the
corrective free collector hit its450s stage limit and its16 controlled endpoints
were never attempted. The later [additive completion](../analyses/root-corrective-reduction-sft-live-2026-09-09/completion/REPORT.md)
ran those exact16 coordinates without training/reselection/rerolls:5 correct/14
available/16 planned. Only one faithfully computed a supplied-map scalar, matching
the unchanged root's one; four other successful answers reacquired scoped labels.
The copied-map correction was not reproduced. Lower supervised loss did not
establish autonomous reachability or faithful reduction. Original and additive
inventories, NULLs, clocks and physical versus replayed acquisitions stay separate.

The [restart study](../operations/2026-09-09-allocation-5780/artifact-restart-audit-report.md)
provides a stronger uptake signal on the same16 source states: quoted genuine
history10/16 correct and12 faithful supplied-state reductions; references to the
same files3/16 correct with zero archived-state reads and42 new child calls;
inline metadata6/16 planned with only one faithful reduction and two native empty
finals. Twelve quote-arm programs reconstructed all16 actual labels, including four
width4 sources requiring multiple historical pieces. Two faithful results inherited
wrong child classifications. The quote bundles producer code with observations and
changes prompt length; all arms use fresh roots, not exact old native histories.
This motivates a visibility factorial, not a general memory or summarization claim.

### Separating code quotations and observations

The [content64 audit](../operations/2026-09-09-allocation-5780/state-content-factorial-audit-report.md)
finds genuine old-state use3/32→18/32 and faithful supplied-state scoped reduction
3/32→16/32 with actual observations visible. Dataset correctness changes only
14/32→15/32. Producer quotes without observations mostly cue new acquisition
(17 child calls in13 P1V0 rows); they are not persistent evidence themselves.
Full width4 old-map merging occurs12/32 overall,3/16 V0 and9/16 V1, as corrected
in the [authoritative erratum](../operations/2026-09-09-allocation-5780/state-content-factorial-audit-report-erratum.md).
Four exposed context clusters, altered prompt lengths, unchanged common API
example/files and two actual timeout NULLs limit causal scope. Read the report
with its erratum; original bytes remain preserved.

### Whole-sequence training helps some answers, but through mixed strategies

The [joint training audit](../operations/2026-09-09-allocation-5780/joint-state-reduction-sft-audit-report.md)
finds8/16 planned free answers correct after training the acquisition-to-answer
sequence, versus6/16 for reduction/stopping training and2/16 unchanged. Available
finals number12,14 and15 respectively. Only one successful free answer per policy
uses the intended live-map scalar followed by a strict final. Other trained
successes genuinely use returned labels through copied lists or manual counting;
those remain valid task successes, not proof of the intended state-carrying program.

The improvement is concentrated in union queries on four previously used contexts.
Joint training used20,064 supervised target tokens versus5,024, and its free
evaluation made401 physical requests versus281 and77. Equal four-update counts do
not match the training dose or inference cost. The
[checkpoint wording erratum](../operations/2026-09-09-allocation-5780/joint-state-reduction-sft-audit-report-erratum.md)
preserves the final four-update result while correcting the earlier checkpoints'
step counts. A fixed-policy transfer test is accepted, but supplies no result yet.

## What remains unknown

The visibility study's eight dataset errors are the same two train-01 questions in every cell and
follow the reused map's two label errors; upstream semantics dominate those endpoints. It remains
unknown whether true inline-only availability changes uptake, because file access remained available
and was used in all inline traces. No observed case establishes a correct displayed scalar followed
by an incorrect final answer, so automatic finalization is not the supported primary diagnosis.

## Smallest discriminating next experiment

The64-endpoint producer-quote × actual-observation visibility comparison is now
independently audited. All files, metadata and common API
example remain identical; it measures extra inline visibility, not exclusive access.
Its16 states are exploratory reused contexts, so any effect requires genuinely new
context replication. Joint acquisition/reduction/stopping SFT has completed with
the qualified mixed-strategy result described above. The accepted fixed-policy
transfer tests the same three policies on64 root-catalog-new source records;
those records remain child-training-exposed. A separately prepared operator
diagnostic compares role wording and genuine predicted evidence on two QSR
training contexts. Measure actual state use, overwriting, scoped execution,
completion and full costs. Never insert host gold, repair answers, or count nested
seeds as new contexts. Query-sensitive RLVR is a complementary question,
not evidence that a failed narrow SFT recipe should simply receive more epochs.

## What would justify a stronger claim

Promote a reduction diagnosis if correct supplied maps reliably produce executed correct scalars and
strict final gains on new contexts. Revise toward child semantics or width if supplied maps pass but
sampled maps fail. Prioritize interface/reducer training if supplied maps still fail through
container misuse or reduction, and retire the automatic-finalization diagnosis unless a genuine
correct-scalar/wrong-final case appears.
