# B05 singleton decomposition implementation plan

> Inline execution of the approved CPU-only external sidecar. No source repository, sealed collector, model, environment, or GPU mutation.

Goal: six new normalized stages, two at width 6/12/20, two repeats, fixed whole-list/whole-vector/singleton-union comparison. Exactly 176 physical calls: 152 scalar + 12 list + 12 vector. All stages and candidates remain scheduled regardless of answers.

Architecture: reuse the qualified B05 native request/decode/collector and V3 lifecycle; add only pure projection/scalar validation, stage aggregation, new input freeze, and explicit owner accounting. This external path is the user-approved isolation boundary; no Git worktree or installs.

Global constraints: released base Qwen3-4B-Instruct-2507; T=.5, four stage workers, 8192 prefix+output bound; scalar cap16, full caps384; science900/owner1000/external1100. Generation202609420000..5, root decode202609430000..11; scalar seed=rootseed+1000+candidateindex. No optimizer. MAIN sole launcher. Full raw native per-call receipts and final actual-dispatch qualification retained.

Task 1 — scalar interface and frozen inputs (CPU).

- [ ] Write `test_singleton.py` literal-boolean/partial-missing test; run RED before `interface.py`.
- [ ] Implement `singleton_prompt`, `parse_scalar`, and `singleton_union`. Never convert missing/invalid to false; keep unknown and invalid-known counts separately, IDs None unless every scalar is valid.
- [ ] Add `study.py`, `prepare.py`: freeze all six public roots, projected prompts, requests, schedule and token audit before computing host gold with both existing solvers. Pin all known B05 public root/ID exposures, source hashes and native dependencies. Verify scalar true/false+EOS fits16 label-blind.

Task 2 — collection/accounting and MAIN handoff (CPU).

- [ ] Add thin `collect.py`, `metrics.py`, `owner.py` using immutable native transport and repaired lifecycle. Implement 176 physical-call and 36 stage-output accounting, all12 per-arm denominator, context-paired comparisons, unknown cost and length-stop inventories.
- [ ] Run actual local HTTP fixture through the real Collector with native token IDs, scalar16/full384, model/seed/prefix/usage and response-hash validation; exercise actual owner module bindings. No GPU or credentials from live services.
- [ ] Write `RUNBOOK.md`, `CPU_TESTS.json`, immutable `CPU_READY.json`; execute actual `owner.py verify` and send hashes/argv to MAIN. No automatic run or polling.

Spec: `ideas/2026-09-13-normalized-singleton-decision-screen.md`, amended by MAIN: scalar16, science900/owner1000/external1100, explicit fixed numeric seeds above. No broader RL implementation.
