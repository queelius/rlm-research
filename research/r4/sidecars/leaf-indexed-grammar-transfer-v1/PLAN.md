# Leaf indexed grammar transfer implementation plan

> Execute inline using executing-plans and TDD; no subagents or GPU calls. Parent-approved DESIGN.md is authoritative. Sources outside this additive sidecar are read-only.

Goal: freeze the160-call factorial with fresh SST exclusion and conditionally bind the fixed indexed checkpoint.

- [ ] Write focused failing tests: exact160/eight-cell allocation and SST exclusion; common input/grammar-only delta and gold independence; strict duplicate/cardinality handling; actual collector wire/alias/cost checkpoint path; checkpoint identity rejection.
- [ ] Implement study.py using the pinned private anchor helper/qualified collector. DATA.json stores one permutation and full source provenance; make_request changes only alias and grammar state around the established representation contract. score_coordinate reuses complete-output scoring; summarize groups by dataset/weight/representation/grammar.
- [ ] Implement driver.py: CPU prepare/render/schema validation, immutable spec verification, conditional old/indexed binding, version/live-alias preflight and bounded160-call collection. Reuse typed HF/vLLM rendering and exact-wire capture; do not start a service.
- [ ] Run the focused tests and real CPU request/schema compilation. Freeze DATA/REQUESTS/SPEC and PREPARED.json with source hashes. Preserve the seed collision audit and max prompt+3072<=8192 evidence.
- [ ] Only after immutable indexed RESULT/SELECTION/state authenticate, publish WEIGHTS.json and final READY.json; bind new endpoint descriptors separately. Parent reviews source and launches.

Files: DESIGN.md, PLAN.md, README.md, study.py, driver.py, test_study.py; generated immutable DATA.json, REQUESTS.json, CPU_QUALIFICATION.json, CPU_TESTS.json, SEED_AUDIT.json, SPEC.json, PREPARED.json, then WEIGHTS.json/READY.json. No repository branch changes: the user-designated sidecar is the isolated workspace.

Verification: CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q -p no:cacheprovider test_study.py; then driver.py prepare. No broad test suite or dependency/environment mutations.
