---
schema: recombination-decomposition-pilot-design-v1
created_utc: 2026-09-12T22:00:46Z
status: proposed_not_implemented
decision: use_candidate_b05_for_a_bounded_mechanism_screen
gpu_calls_max: 128
gpu_time_target_minutes: 10
---

# A bounded recombination screen using an existing exact ETL task

## Decision

Use the existing **Versioned ETL Catalog Planning (B05)** candidate for one
mechanism screen. Do not build a new customer/purchase benchmark yet. B05 already
has three independent local database queries, typed complete-relation reports,
an exact cross-stage join, a combiner that trusts displayed reports rather than
repairing them from hidden source, and separate malformed / invalid-claim /
claim-valid-wrong / correct outcomes. This is the smallest existing asset that
can distinguish a bad local interface, lost local facts, and a bad global join.

This is a candidate-only generator, not an admitted benchmark. It has no Qwen
calibration, no independent campaign verifier, no generated IID/OOD split, and a
known feasible-spine construction that may create shortcuts. A positive screen
would justify data freezing and a planner-learning pilot; it would not establish
learned decomposition or generalization.

## Existing assets and current readiness

- Candidate root: `data/candidates/sol-generator-tournament-v1/builders/05-program-dataflow-database`
  in `structured-decomposition-benchmark` at commit
  `c7ee38127e5f37c327b77f518a21f0bab151ff33`.
- Package identity: `metadata.json`; exact semantics and losslessness assumptions:
  `FAMILY.md`; public contracts: `MODEL_VISIBLE_SCHEMA.md` and `schemas/`.
- CPU generator: `src/etl_catalog/generator.py`; two local solvers:
  `solver_reference.py` and `solver_independent.py`; two root solvers plus the
  arbitrary-report path: `solver_reference.py`, `solver_independent.py`, and
  `combiner.py`; exact grading: `grading.py`; prompts: `render.py`.
- Error attribution: `errors.py` supplies omission, capacity-shift, and
  format-substitution reports, while `records.py` records their implied answers.
- Package manifest SHA-256:
  `d975b5acd84d2a8323694f6935cc23d3a3cf05309982e1bbf343c105a0887997`.
- Replayed in this session without model/network calls: 29 focused tests passed;
  three examples/38 generated paths matched; three roots/37 manifest-hashed files
  passed semantic replay. The retained 900-root fuzz is package evidence, not a
  fresh independent rerun.

`rlm-bootstrap` at commit `7f79801073be7799a2318c414f29a764af1a1a0b`
provides stronger materialization and group-split machinery in
`src/rlm_bootstrap/synthetic/{dataset,splits,verify}.py`, and its 36 focused
generator/verifier/end-to-end tests passed in this session. Its existing
`classify-filter-aggregate-v1` task, however, is one monolithic context with
count/conditional-count/distribution/argmax questions. It has no shard report or
cross-partition join, so use its manifest/split conventions later rather than
pretending it tests recombination now. No existing customer/purchase join
generator was found in either repository.

## Frozen pilot before any model outcome

Materialize eight `small` B05 roots by deterministic hash rank from a new seed
namespace. Allocate four roots to open calibration (`chain`, history depth 2) and
four to structural transfer (`hub`, history depth 4); keep candidate count,
budgets, response contract, and model settings fixed. Treat topology plus history
depth as one bundled structural shift, not an isolated depth effect. Record every
generated safe/trusted hash and reject semantic duplicates across arms. Gold and
solver receipts remain host-only.

For each root, issue exactly 16 model calls with the same fixed 4B checkpoint and
sampling policy:

1. one full-input direct call;
2. two independent calls for each of the three local stages (six calls);
3. eight synthesis calls, one for each recombination of the saved local
   alternatives; and
4. one synthesis call using the three exact host reports as an explicitly oracle,
   non-deployable interface ceiling.

Total: 8 roots × 16 = 128 calls. All eight synthesis combinations are retained,
including malformed or invalid reports. They are correlated interventions on one
root, not 64 independent tasks. Run CPU generation/grading first, then one local
4B service with a 10-minute exploratory cap; stop as an honest timeout if current
throughput does not fit. Direct prompts average about 24.7 KB, child prompts
8.7 KB, and exact-report synthesis prompts 28.9 KB in existing small fuzz, so
the time estimate is prospective rather than measured on this family.

## Attribution and planner criterion

For every model call retain raw request/response, token IDs, seed, sampling and
model binding, finish reason, usage, parser status, and exact source hashes.

- **Local interface failure:** malformed or internally invalid child JSON.
- **Lost local fact:** claim-valid local relation differs from the exact relation;
  report the omitted/changed row or field and the host combiner's implied answer.
- **Bad join/synthesis:** all three displayed reports imply the exact answer but
  the synthesizer returns another valid or invalid answer.
- **Interface ceiling failure:** oracle reports are supplied correctly but the
  synthesis answer is wrong; this limits claims about planner learning.

Only prepare a planner update if at least three of four open roots have both a
winning and losing *claim-valid* recombination and changing one local alternative
changes the report-implied terminal reward. A planner observation may contain
only public root constraints, component identities, and already generated local
reports; it may not contain gold, solver receipts, error labels, or the selected
answer. Train/held roots are the unit of analysis. Compare held reward against
the competent fixed decomposition, direct full-input baseline, and oracle ceiling.

Promote to a training pilot if the direct and oracle controls are non-degenerate,
local alternatives provide the frozen contrast above, and held topology/depth
does not collapse the typed interface. Revise toward better local extraction if
lost facts dominate. Retire this formulation if direct full input is uniformly
correct at lower cost, oracle synthesis fails broadly, or the feasible spine makes
the answer recoverable without the intended local computations.

No data were generated and no model/GPU call was made for this design.
