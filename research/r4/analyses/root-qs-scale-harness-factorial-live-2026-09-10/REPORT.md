---
schema: root-qs-scale-harness-factorial-failure-audit-report-v1
status: terminal_failure_diagnostic_complete_no_scientific_success_claim
planned: 64
native_authenticated: 38
strict_correct: 9
faithful: 12
faithful_and_strict: 7
null: 26
---

# Scale64 terminal failure diagnostic

The run is not a completed scientific experiment: parent exit was 1 and owner `complete` was false.
The exact relayed terminal artifacts nevertheless prove release, no active GPU process, and both
policy stages `work_complete=true`, so the frozen failure-diagnostic method authorizes bounded audit.

## Native outcomes and failure taxonomy

All 64 planned cells are retained. The qualified native reader authenticated 38 terminal paths: 9
strictly correct and 29 observed wrong. Sixteen of those wrong paths have authenticated empty finals;
they are observed failures, not NULL. The remaining 26 cells have no episode/result because every one
hit the same `asyncio.wait_for` `TimeoutError` in `native_slot` after roughly 181–186 seconds; those are
NULL, not wrong answers. Owner inventory therefore decomposes as 22 nonempty native finals, 16
authenticated empty finals, and 26 timeouts.

Availability collapses with size: 15/16 paths authenticate at size16 (8 strict), 11/16 at size64 (1
strict), 9/16 at size128 (0 strict), and 3/16 at size256 (0 strict). This makes the intended scale and
survival contrasts mostly unidentified.

## Manual semantics

Every one of the 38 authenticated paths was manually reviewed from its actual root programs and
parent-linked tool observations. Trusted host labels are stored separately from policy evidence.
Counts on the 38 observed paths are: acquisition 31, retained complete decoded map 20, requested J1
operator/scope/targets faithfully executed 12, final uses observed state 19, full aggregation 19,
faithful 12, and faithful-plus-strict 7.

At size16, 8/15 observed paths are faithful and 6/15 are faithful-plus-strict. At size64, 4/11 are
faithful and 1/11 is faithful-plus-strict. No observed size128 or size256 path is faithful. The five
faithful-but-wrong paths have complete observed maps and execute the requested reducer; their wrong
scalars are consistent with child-label errors rather than root reduction errors. Unfaithful terminal
answers include global instead of same-user conditions, summing the wrong category, counting instead
of weighting, retaining only the last batch, malformed/truncated child maps, and terminal zeroes after
failed acquisition.

For the primary paired root effect at size16: cumulative has all four cluster pairs and mean effect
0.00; raw has three complete pairs, mean +0.333, with planned-denominator bounds [0.00,+0.50]. At
size64 cumulative has three pairs, mean +0.333 and bounds [0.00,+0.50]; raw has one pair, mean 0 and
bounds [-0.75,+0.75]. Size128 and size256 contrasts are dominated by NULLs; the frozen survival DID
and focused large-size harness claim are not identified. These descriptive observed-pair values must
not be promoted as a successful factorial result.

## Cost and limitations

The physical disk union contains 779 model attempts: 358 unchanged-root, 181 sft6-root, and 240 fixed
child. Known usage is 2,440,593 input, 148,713 output, and 2,233,920 cached tokens; 21 attempts lack
each usage field. Billing is unavailable. The attempt consumed 1,850.7 parent seconds. The large
timeout/empty-final load, correlated nested clusters, only four clusters, child-label errors, and
harness bundle interpretation prevent a generalization or isolated-memory claim.

The clearest follow-up is a smaller timeout-safe replication focused on sizes16/64, or the frozen
transparent supplied-plan ceiling, rather than spending another run on size256 before the per-episode
deadline/call amplification is controlled.
