# Independent audit method: exact operator SFT6 to SFT24

Frozen after training launch and after MAIN disclosed that checkpoint 7 exists with a real first
continuation update. The auditor has not inspected checkpoint 7 or any later weight, metric, NLL, or
readout outcome. This is therefore outcome-unseen for steps 8--24 and all readouts, but it is not a
prelaunch registration and is not blind to successful initiation. The auditor did not author this
training/readout implementation; the auditor did audit the SFT6 recovery and recommended the common
857 start used upstream.

## Question and fixed comparison

Does continuing the exact persisted SFT6 policy through 18 more full passes (Adam steps 7--24) make
the learned operator routine reachable at inference, rather than merely further reducing teacher
loss? Training must restore checkpoint 6 adapter, optimizer moments and RNG without reset, replay the
same immutable 72 full trajectories once per update, and select fixed step 24 without performance
selection. The contemporaneous readout compares retained SFT6 and SFT24 on the already frozen 96
full endpoints and 24 first-action probes. The same 72-row corpus means dose is tested, not training
data breadth.

## Training integrity checks

1. Pin READY, complete source/input closures, fixed corpus, checkpoint 6, parameter map, evaluation
   plan, start/command/owner receipts, environments and model manifest before outcome analysis.
2. Independently verify the 504 source-derived ordered trainable names/shapes against every restored
   Adam state. Names were reconstructed with the pinned meta-model and were not historically logged;
   report that limitation. Check checkpoint 6 moments bytewise through the restorer receipt, exact
   Adam recipe, finite moments, one parameter group, RNG restoration after diagnostic/setup and
   immediately before update 7.
3. For steps 7--24 require a continuous state-hash ancestry from checkpoint 6; exact identity/corpus,
   epoch=step, cursor=0; all checkpoint member hashes; 504 optimizer states whose step equals the
   checkpoint ordinal; one unique 72-example order containing the immutable corpus exactly once; and
   finite nonzero adapter delta. No missing checkpoint may be replaced by a later one.
4. Recount actual exposure ledgers from saved metrics: 18 x 72 = 1,296 example exposures, expected
   5,832 root-turn and 411,246 current-action target-token exposures. Recheck input/label/loss-mask
   alignment and source span partition from the frozen corpus. Training loads or calls no child model;
   captured child outputs remain historical teacher context, including their errors.
5. Report all 18 weighted CE, role-specific NLL, gradient norm, adapter delta and elapsed checkpoint
   values. Post6 and post24 teacher NLL use only the fixed 12 source-derived first-prefix probes and
   are diagnostic support measurements, not task performance or checkpoint-selection criteria.
   Preserve whether values are measured pre- or post-update.
6. Verify SELECTION is fixed checkpoint 24 and RESULT/owner terminal agree on 18 real added steps,
   nonfresh optimizer, no child update/load, release and elapsed optimizer/checkpoint versus NLL time.
   Partial completion remains infrastructure evidence, never a substitute policy.

## Readout amendment and scoring

The 96 full endpoints and 24 first-action probes were frozen before training, but the readout source
was not READY when this method was written. Before reading any readout outcome, add a source/timing
amendment pinning its owner, service, collector, prompts, native token contracts, exact two-policy
checkpoint bindings and planned NULL inventory. If sampling begins first, disclose that timing rather
than claiming a prospective source seal.

For full endpoints, authenticate actual native prompt/final/model/usage and score only exact
`Answer: N` against frozen host gold. Completed wrong/malformed responses are zero; missing,
unfinished tool branches or native-inconsistent responses are NULL with bounds. Compare SFT24 to
SFT6 in paired coordinates on the planned denominator and jointly available subset, stratified by
new versus exposed panel, operator, scope, context and zero versus nonzero gold. No answer repair,
sampled-code reexecution, best-checkpoint selection or dropped NULLs.

Separately inspect actual child acquisition, returned-label use, width aggregation, scope/reduction,
error recovery and stopping. A correct scalar without live dataflow is task success but not the
hoped-for mechanism. First-action probes measure syntactic intent at a frozen teacher prefix; they
do not execute a child and cannot demonstrate acquisition or reduction. Report nonzero and
best-constant-compatible answers explicitly.

Physical training time, diagnostic time, readout requests/tokens, historical teacher-capture costs
and hypothetical standalone totals remain separate. Local provider billing/cache use are unknown
unless directly recorded. Four exposed evaluation contexts and source-prepared contexts limit
independence; no generic operator-learning claim follows from this panel.
