# GEPA × three-route sidecar design

Status: approved adapter-only boundary, 2026-09-02 UTC.

## Purpose

Prepare, but do not launch, a matched-budget comparison of three harness-search arms over the
sealed three-route qualification task:

1. the frozen seed harness;
2. GEPA optimization;
3. equal-budget deterministic random/local mutation.

The sidecar owns study orchestration, lineage, budget accounting, checkpoint/resume, and analysis.
It does not own corpus generation, the production exact verifier, model serving, or GEPA source.
Those remain immutable external dependencies.

## Hard boundary

The current `rlm-bootstrap` checkout contains the Task 2 generator but no persisted authenticated
36-group/108-task corpus, production Oracle-B/output-verifier provider, or Task 9 authenticated
preparation/runtime bundle. Therefore this sidecar must refuse a research launch until a future
provider satisfies the dependency contract below. It must not reconstruct Task 9, accept caller
assertions in place of authenticated bytes, or silently use fixture data.

CPU fixture tests exercise engineering behavior only. Fixture outputs carry
`evidence_class="engineering_fixture"`, live outside the research attempt namespace, and cannot be
promoted or analyzed as research evidence.

## Immutable dependencies

- GEPA repository: `/project/alex_phd/research-cache/repos/gepa`, commit
  `0632cdb5dcc052e690eab439e1b4a7e3e9cfe407`, MIT.
- RLM-bootstrap source: `/project/alex_phd/repos/rlm-bootstrap/.worktrees/adaptive-context-tranche1`.
  The three-route generator is pinned to commit
  `66fcd3c` (`Generate three-route qualification contexts`); the checked-out descendant may differ
  only if the manifest explicitly records and authenticates the full source commit.
- Sealed config path:
  `configs/studies/three-route-open-qualification-v1.toml`.
- Exact model/harness/corpus/verifier identities are launch inputs and must match the future provider
  descriptor byte-for-byte and by SHA-256.

## Future provider contract

The launcher accepts one JSON descriptor and one importable Python provider. The descriptor is
strict JSON with duplicate keys rejected and contains:

- `schema_version=1`, `evidence_class="research"`;
- absolute `corpus_path`, `corpus_sha256`, `corpus_id`, `generation_inputs_id`, and exactly 108
  unique tasks in 36 unique groups;
- `corpus_loader_provider="module:function"`, `corpus_loader_sha256`, and
  `corpus_loader_contract="three-route-authenticated-corpus-loader-v1"`;
- `verifier_provider="module:function"`, `verifier_sha256`, and
  `verifier_contract="three-route-exact-output-v1"`;
- `runner_provider="module:function"`, `runner_sha256`, and
  `runner_contract="three-route-harness-runner-v1"`;
- `proposal_provider="module:function"`, `proposal_sha256`, and
  `proposal_contract="three-route-gepa-proposer-v1"`;
- absolute `seed_candidate_path`, its SHA-256, and the exact editable component-name sequence;
- source/config/GEPA commits and file hashes;
- model, tokenizer, renderer, harness, launch-bundle and dataset identities;
- declared train, development, and confirmatory group IDs with no overlap.

The verifier callable has signature
`verify(task: Mapping[str, object], output_text: str) -> Mapping[str, object]`. It must return exactly
`task_id`, `valid`, `exact`, `reward`, `reason_code`, `observed`, and `gold_sha256`; reward is binary
and equals exactness. The runner callable has signature
`run(candidate: Mapping[str, str], task: Mapping[str, object], request: Mapping[str, object]) -> Mapping[str, object]`.
It returns output text, trace/event identities, model-call count, input/output/cached tokens, elapsed
seconds, provider/model/renderer/harness identities, and terminal status. Sidecar code validates
these envelopes and independently recomputes task/output/event hashes.

The corpus loader callable has signature
`load(corpus_path: str, descriptor: Mapping[str, object]) -> Sequence[Mapping[str, object]]` and must
perform the upstream authenticated replay before returning public task envelopes. The proposal
callable has signature
`propose(candidate, reflective_dataset, components, request) -> Mapping[str, object]`; its envelope
contains the proposed component texts plus proposal-model calls/tokens/time and endpoint identity.
Both are hash-bound source dependencies. The seed candidate is strict JSON containing exactly the
declared editable string components; no sidecar default can substitute for it.

## Study design

The provider’s group split is authoritative and immutable:

- exploratory train groups: GEPA and random/local mutation proposal generation;
- exploratory development groups: selection, early-stop, and pivot decisions;
- confirmatory groups: sealed until an explicit `confirm` command; exactly one final evaluation per
  arm after candidate selection.

Task members of a group never cross splits. All arms use identical task order, decoding request,
model endpoint identity, and budget unit. The budget is total metric evaluations: one candidate-task
pair consumes one unit whether cached, successful, invalid, or failed. Model calls, tokens, and wall
time are secondary audits, not substitutes for metric units. The frozen arm is evaluated once on
each relevant split; GEPA and random/local mutation receive the same proposal-evaluation budget,
train/development schedule, and terminal candidate evaluation.

Random/local mutations use a pinned seed and deterministic operators over the same candidate
components GEPA may edit. Operators are logged before evaluation. The random arm cannot inspect GEPA
proposals or scores.

## Lineage and immutability

Every proposal, evaluation, checkpoint, and decision is one canonical JSON record with a SHA-256 ID
over its semantic content and explicit parent IDs. JSONL ledgers are append-only; resume validates
the complete hash chain and rejects truncation, mutation, duplicate IDs, changed inputs, or changed
budget. Checkpoints are content-addressed snapshots written through a temporary file then renamed.
The terminal result binds every input hash, ledger tail, selected candidate, and endpoint.

Each evaluation records arm, split, task/group/candidate/proposal IDs, parent candidate, mutation
operator, request and output hashes, verifier envelope, calls, tokens, elapsed time, endpoint
identity, monotonic timestamps, and failure classification. Private gold data is never written in
clear text; only verifier reason and gold digest are retained.

## Preregistered endpoints

Primary confirmatory endpoint: macro exact accuracy over confirmatory groups, with the group as the
resampling unit. Primary contrast: GEPA minus frozen. The equal-budget random-minus-frozen and
GEPA-minus-random contrasts are multiplicity-aware secondary endpoints. Report 95% group-bootstrap
intervals using a frozen bootstrap seed and route/organization/token-band strata.

Audits: invalid rate, task coverage, model calls, input/output/cached tokens, elapsed seconds,
accuracy per 1,000 output tokens, route accuracy, and train–development gap. No task is omitted from
denominators. Infrastructure failures are separate from incorrect answers and trigger the declared
retry-free failure policy.

## Stop and pivot criteria

- Stop before any model call on dependency/hash/schema/split mismatch.
- Stop an arm when its metric budget is exhausted; never borrow from another arm.
- Stop the study if any task order, endpoint identity, decoding request, verifier identity, or
  candidate component changes after the run seal.
- Stop if infrastructure failures exceed 5% of attempted evaluations or any private gold value is
  exposed outside the verifier process.
- Exploratory futility pivot: if GEPA’s best development macro exact is not at least frozen +0.02
  after 50% of its budget, finish the already-started batch, checkpoint, and recommend mechanism
  audit rather than confirmatory launch.
- Overfit pivot: if GEPA train gain exceeds development gain by more than 0.10, freeze proposals and
  inspect lineage; do not touch confirmatory tasks.
- Positive launch criterion: GEPA development gain at least 0.03 over frozen, no worse than random,
  invalid-rate increase at most 0.02, and all lineage/cost audits clean.

## Components

- `study.json`: preregistration, budgets, split policy, seeds, endpoints, and stop rules.
- `dependency-contract.json`: exact future provider schema and pinned external sources.
- `source/gepa_three_route/`: strict schemas, hashing, adapter interfaces, ledger/checkpoints,
  matched-budget scheduler, deterministic mutation control, preflight, and CLI.
- `tests/`: CPU-only unit and synthetic integration tests; no network, ports, GPUs, or official repo
  writes.
- `manifest.json`: hashes of all immutable sidecar files and external input pins.
- `RUNBOOK.md`: CPU preflight, actionable refusal diagnostics, future launch command, outputs, and
  recovery procedure.

## Error reporting and testing

All refusal paths write/print a single strict JSON diagnostic with `ok=false`, stable `code`, human
`message`, `remediation`, and structured `details`; exit status is nonzero. Tests begin red and cover
duplicate-key rejection, dependency drift, split leakage, equal budgets, fixture exclusion,
append-only lineage, resume equivalence, cost metadata, stop/pivot decisions, and a synthetic
end-to-end run. CPU preflight authenticates sidecar files and external pins without importing or
writing either cached repository.
