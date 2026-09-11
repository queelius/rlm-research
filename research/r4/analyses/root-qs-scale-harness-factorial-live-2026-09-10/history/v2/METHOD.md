---
schema: root-qs-scale-harness-factorial-audit-method-v1
status: prospective_frozen_before_outcomes
prepared_utc: 2026-09-10
planned_endpoints: 64
analysis_unit: cluster
clusters: 4
sizes: [16, 64, 128, 256]
root_policies: [unchanged, sft6]
harness_packages: [raw_batch_20000b, cumulative_4096b]
primary_outcome: faithful_and_strict
terminal_relay_required: true
---

# Prospective native and semantic audit method

## Gate and availability

No outcome, trace, role ledger, or physical-call record may be opened until MAIN supplies the exact
parent `EXIT.json` and its SHA-256 plus the exact `OWNER_TERMINAL.json` SHA-256. The reader verifies
exit code zero, no timeout, clean owner completion/release, no owner error, and an empty reported GPU
process list before outcome access. A missing or unauthenticated native result is `NULL`. An
authenticated empty or malformed final is observed and strictly incorrect.

Native authentication reuses the qualified QS Responses reader and frozen renderer: request prefix,
coordinate, seed, binding/checkpoint, role record, native response, completion token IDs, tool state,
and final text must agree. The 64 planned cells remain in the denominator.

## Frozen estimands

The primary outcome is `faithful_and_strict`. Secondary outcomes are strict scalar correctness,
native availability, acquisition, complete-map retention, requested J1 fidelity, observed-state use,
full aggregation, child-label accuracy, and root/child physical usage.

Report fixed6-minus-unchanged paired effects by size and harness package. Report survival DID as the
size-256 root effect minus the size-16 root effect, separately by harness. Report the package effect
for fixed6 at sizes 128 and 256. The policy × size × package contrast is exploratory. Each contrast
uses the four clusters as the correlated units; endpoints and nested prefixes are not treated as
independent observations. Complete-pair estimates accompany planned-denominator worst/best bounds for
NULL pairs. These are descriptive mechanism diagnostics, not population confidence intervals.

## Manual semantic review

For every available endpoint, a reviewer reads the complete authenticated root programs and their
parent-linked tool observations in order. The evidence pack exposes every parseable growing child
label map and the requested J1 operands, while placing trusted host labels in a visibly separate
oracle section. No keyword or syntactic-program heuristic supplies a fidelity verdict.

The reviewer records five booleans, a classification, and a concrete note:

- `acquisition`: at least one actual child-returned label map was obtained.
- `retained_complete_map`: immediately before reduction/finalization, the observed state retained a
  decoded label for every requested record ID.
- `requested_operator_scope_target_faithful`: actually executed logic implements the frozen J1 rule:
  find users with at least one `target` record, then sum weights of all their `target_b` records over
  `ALL` scoped users. Variable names and implementation style are irrelevant.
- `final_uses_observed_state`: the final scalar flows from actually observed child maps/state, rather
  than a guessed, copied, or hard-coded number.
- `full_aggregation`: acquisition and reduction cover all `size` records, not a subset or last batch.

`faithful` is the conjunction of those five fields. `faithful_and_strict` also requires the exact
native `Answer: N` final. Semantic faithfulness may be true while strict correctness is false when
child labels are wrong; host-oracle child-label accuracy is reported only as a diagnostic. For an
available endpoint, missing manual fields are an audit error. For an unavailable endpoint, semantic
fields remain `NULL`.

## Harness evidence and cost

The audit retains raw session-harvest rows, bounded-view events (raw/visible hashes and byte counts
when present), programs, tool observations, map growth, and actual reduction evidence. The harness
contrast is labeled as a bundle: current-batch return plus 20,000-byte raw view versus cumulative
return plus 4,096-byte head/tail view. It is not called an isolated memory effect, and filesystem
access remains possible in both arms.

Cost is the physical union across both root services and child calls, deduplicated by returned
provider request ID when available and otherwise by the immutable physical record. Root and child
roles, attempts, returned status, known/unknown token fields, unmatched role intents, elapsed owner
time, and billing availability are reported separately. Missing usage is unknown, never zero.

## Planned post-terminal artifacts

After the relay gate, the reader produces a raw authenticated audit, a per-endpoint evidence pack, a
manual annotation template, a validated merged semantic audit, paired contrasts/DIDs, a report, and a
final hash seal. The evidence pack and annotations remain reviewable independently of aggregate code.
