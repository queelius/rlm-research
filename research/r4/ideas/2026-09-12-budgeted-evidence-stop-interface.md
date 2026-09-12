---
schema: rlm-decomposition-experiment-design-v1
created_utc: 2026-09-12
status: proposed_ready_for_bounded_cpu_preparation_no_gpu
question: can_the_root_choose_what_evidence_to_delegate_and_when_to_stop
new_intervention: stateful_budgeted_record_id_selection_plus_explicit_finish_receipt
arms: [eager_all16, budgeted_as_needed]
planned_endpoints: 48
gpu: one_A100_40GB
owner_cap_seconds: 1000
outer_cap_seconds: 1100
training: none
claim_scope: interface_screen_on_two_research_exposed_contexts
---

# Let the root choose evidence scope and stopping

## Why this is the next architecture screen

The strongest root result did not learn decomposition: the six-update controller reached 57/72
exact and 29/72 faithful-and-exact versus 27/72 and 2/72 for fixed24, but every prompt explicitly
prescribed the operator sequence. The latest explicit-interface qualifier made 4/6 finals correct
with a helper versus 0/6 without one, yet failed its gate: both arms repeated identical actions,
one correct final used an unfaithful stale-variable calculation, and the no-helper arm looped on an
invalid import. The additive prefix audit established that all initial prompts were actually
correct, so another prompt-prefix repair is not the experiment.

Keyed helper returns are useful plumbing, not the missing decision. Compact key-to-label replies
saved 22.5% output tokens with only a 0.78-point record-accuracy change, while the whole-task
`classify_all()` handoff never demonstrated a gain because the root misused the API. Supplying
different complete maps also changed downstream outcomes: batch4 maps produced 18/24 correct
versus 12/24 for batch16, with 7 paired wins and 2 losses among 23 jointly observed endpoints even
though 22/24 initial root responses matched. That establishes that evidence state matters, not that
the root can decide what evidence to acquire.

The new question is narrower and genuinely different: **can the existing SFT6 root choose direct
solving versus delegation, choose record IDs, accumulate returned state, and declare when it has
enough evidence?** No operator, subset, label, answer, or missing argument is selected by the host.

## Paired intervention

Use the existing 24 downstream coordinates: six operation families across the two
`question-sensitive-sft-train-05/06` contexts, two repeats each. These are intentionally a cheap,
research-exposed interface screen, not fresh-context generalization. Use fresh paired root seeds
`202609121500..202609121523`, the frozen SFT6 root checkpoint, identical public records/questions,
and the same authenticated batch4-derived 16-ID map for both arms at each context/repeat.

Both arms expose the same synchronous stateful functions:

```text
classify(record_ids) -> {requested_id: saved_native_label, ...}
finish(answer, evidence_ids) -> {accepted: true, declaration_sha256: ...}
```

`classify` accepts only nonempty, unique, in-context IDs. It returns the requested projection of
one previously sampled native helper map, preserves wrong labels byte-for-byte, rejects duplicate
acquisition, and never calls a child. `finish` checks only that `answer` is an integer and every
declared evidence ID was actually returned. It neither checks nor renders the correct answer. The
root must still implement the requested filtering/aggregation in ordinary Python and emit its own
`Answer: N` final; the audit requires that N equal the declared value.

- **Eager-all16:** the same `classify` function accepts only the complete ordered 16-ID inventory.
  The model still chooses delegate versus direct and when to finish, but not evidence scope.
- **Budgeted-as-needed:** the function accepts any subset, at most four calls and at most 16 unique
  IDs total. The root may finish without delegation, request one subset, or acquire more disjoint
  subsets after observing labels.

This changes only the admissible evidence-selection action. It does not supply a task operator as
the earlier operator-composition prompts did, and it does not compare another helper
hyperparameter. The returned labels are identical whenever the requested ID is identical.

## Measurements and frozen interpretation

Primary: paired exact-final wins/losses and all-planned correct counts. Secondary: available finals,
correct-and-faithful computation from inert program review, agreement with the requested operation
evaluated on the actually returned map, valid `finish` use, direct/delegate choice, rounds, distinct
IDs, repeated/invalid actions, turn-limit finals, and root calls/tokens/time. A host-only
dependency audit may report whether the acquired IDs suffice for the requested calculation, but its
result is never placed in a prompt or callback.

Promote to a fresh-context test only if budgeted-as-needed (a) loses no more than two exact answers
and no faithful-and-exact answers relative to eager-all16, (b) has at least six correct-and-faithful
endpoints spanning both contexts that finish after requesting at most 12 IDs, and (c) does not add
material unavailable or repeated-invalid-action failures. If it requests all16 almost everywhere,
or any apparent gain is only wrong-operator coincidence, retire the interface rather than train a
selector. This is an exploratory Pareto screen, not an equivalence margin.

## Provenance and no-oracle boundary

The callback may read only `HELPER_MAPS_V2.json` SHA-256
`31aee0607c6457e300c5c39181959c6318ddfc855e7337fff358285382e9e3ee`, whose values trace to
physical batch4 child responses. It must not import or read `HOST_GOLD`; only the external scorer
may do so after the final. Every callback receipt records coordinate, requested ordered IDs,
returned-content hash, source call paths/hashes, cumulative state, and whether `finish` was valid.
Unsupported calls fail and remain counted; there is no answer fallback, label repair, oracle reply,
resampling, or silent drop.

Pinned starting points:

- downstream READY `45da8b2e4fccd931b4ed4086ceb0e996ab365b34196b31f28f4f026737d7a955`;
- downstream study/map interface `9a62572a...` / `80f9a5fb...`;
- existing downstream result `df89165f24e45fc5cf0c45cbda91c69db2edf3ac7341d9e740fbe90930dec524`;
- interface interpretation/prefix addenda `2de50fc8...` / `e870a87b...`;
- compound-operator audit `e4d3f073...`.

Replay means actual child calls and native child tokens are zero in this experiment. Report logical
requested labels/rounds and the old physical map-generation costs separately; do not claim an
end-to-end speedup. Based on the prior 72-endpoint replay owner taking 801.3 seconds, cap this
48-endpoint screen at 1,000 owned / 1,100 outer seconds, checkpoint each endpoint, and preserve
timeouts/NULLs. Runtime scaling is an estimate, not a guaranteed duration.

## Reuse and next decision

A new additive sidecar can reuse the sealed downstream plan construction, SFT6 binding, root
collector/exporter, scorer, and callback installation. Only the stateful projection/finish shim,
fresh namespace/seeds, and receipts are new. Focused CPU qualification should exercise direct,
subset, accumulation, invalid-ID, duplicate-ID, and finish-with-unseen-ID paths plus both complete
request preparations. No broader framework is needed.

If this screen passes, freeze genuinely fresh QS contexts before any selector training and compare
the learned decision against eager-all16 and a predeclared cheap rule. Do not train on or call the
existing eight protected evaluation contexts merely because their cached maps are convenient.
