# B05 eligible-ID interface implementation plan

Goal: test whether removing metadata output burden improves complete eligible-ID selection on the four already exposed B05 roots. This is an adaptive interface experiment, not learned arithmetic, routing, or benchmark admission.

Approved execution is inline CPU preparation; MAIN alone launches GPU work. All files are additive in this external sidecar. No shared sealed sources are edited.

## Fixed comparison

Primary cached control is the qualified source-visible V3 attempt003, not unqualified V2. Use the identical 24 child coordinates, root shards, seeds, base Qwen3-4B-Instruct-2507 checkpoint, T=.5, 384 maximum output tokens, native renderer, four root workers and qualified V3 lifecycle. Replace only the terminal child output contract: one JSON object with exactly `eligible_ids`, a lexicographically sorted unique list of local implementation IDs. Preserve the complete original public shard and query semantics verbatim. No source/gold-derived eligible list enters a prompt. No child retries or root model calls.

Host lookup computes effective public fields for precisely the claimed known IDs; it does not test eligibility, discard ineligible IDs, insert omitted IDs, or replace claims with an exact relation. It applies the same lookup to both arms. CPU combination evaluates every one of the 32 frozen triples per arm. These are reused-child coordinates on four root contexts, not 32 independent problems. This deterministic arithmetic is a harness/interface intervention, not evidence the model learned arithmetic.

Primary metrics: strict eligible-ID-set exactness over all 24 planned children, plus precision/recall on known valid claims with invalid/unknown separate and denominators reported. Also report diagnostic ID-set precision/recall from parseable full-report outputs even if their metadata sorting is invalid, without changing their official full-report grades. Primary paired interface comparison requires strict validity in each respective contract; no silent sorting or duplicate removal of model ID answers. Secondary: same-lookup CPU plan true-source correctness and report-implied feasibility over all fixed triples. Unavailable/invalid child claims leave dependent coordinates unsupported.

New cost: 24 physical child calls, natural three children plus deterministic host operations per root plan; zero physical or natural root model calls. Max384 remains matched even though actual output token costs differ. Science600, owner700, external800 seconds; no training or checkpoint selection.

## Implementation and verification

- [ ] `interface.py`: render the new terminal contract, strict ID parser, no-filter public-field lookup. Focused regression must preserve an intentionally ineligible local ID, reject duplicate/foreign IDs, and retain the exact public input prefix.
- [ ] `study.py`, `collect.py`, `owner.py`: reuse authenticated V3 service/native/lifecycle with only24 child calls. Actual HTTP fixture exercises saved prompt→native tokens→response→ID claim, original seeds/caps, and real owner aliases. No original contract hook may be installed in this sidecar.
- [ ] `metrics.py`: independent host metrics and both-arm deterministic combinations, original V3 full-report scores retained. No source eligibility feedback to model inputs.
- [ ] `prepare.py`: focused tests, closure, frozen prompt/token inventory, source V3 READY identity; seal only with complete/released/runtime-qualified attempt003 and all24 child native evidence. If unavailable, write one CPU-prepared/PENDING receipt and stop. MAIN handles queue monitoring.

Do not launch the report-only36 branch by implication. If IDs-only preserves poor recall, report the negative result without an exposed-case prompt sweep.
