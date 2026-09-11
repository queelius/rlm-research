# Independent isolated-fix review — 2026-09-09

**Merge verdict: approve the four reviewed files. No material correctness, compatibility, or test issue established.** This is read-only review, not integration approval for unrelated changes or proof of exhaustive correctness.

Reviewed the complete tracked diff and untracked `tests/test_engine_late_usage.py` in `/project/alex_phd/repos/rlm/.worktrees/core-evidence-fidelity-20260909`, at unchanged base `3aeb99d2a6ff125868f0329bfea584de84c1f715`. All four file hashes match [FIX_REPORT.md](FIX_REPORT.md). No worktree source, branch, live experiment, or GPU was changed.

- [engine.py:802](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm/.worktrees/core-evidence-fidelity-20260909/src/rlm/engine.py:802"): the added branch executes only after a response has returned and the original action/run deadline check fails. It validates the envelope before recording usage; malformed usage is rejected before ledger mutation. A valid response exceeding the token limit is still counted once, while the nested suppression leaves the original deadline as the fatal outcome. The normal path remains unchanged. Neither a late answer nor a replacement backend/token error is accepted.
- [observation.py:43](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm/.worktrees/core-evidence-fidelity-20260909/src/rlm/observation.py:43") and [line192](../../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm/.worktrees/core-evidence-fidelity-20260909/src/rlm/observation.py:192"): the executor map is retained separately, and each `_set_truncation` starts from that map plus the current observation-stage omissions. Repeated candidate-fit attempts do not accumulate prior totals again. Fully dropped executor channels remain visible; no executor-loss case adds a new field or changes the old encoding.
- Tests exercise the real engine's next request with bounded capture and an opaque fake environment; the 12 fake-clock cases cover run/action/both deadlines with valid usage, token overflow and malformed envelope/usage. This is scoped evidence without executing generated controller code.

Independent verification: **19 tests passed** in 0.58s ([INDEPENDENT_REVIEW_TESTS.xml](../../../../ARTIFACTS.md#unpublished-files "Not published: INDEPENDENT_REVIEW_TESTS.xml")). Command:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/project/alex_phd/repos/rlm/.worktrees/core-evidence-fidelity-20260909/src /project/alex_phd/envs/rlm/bin/python -m pytest -q -p no:cacheprovider tests/test_observation.py tests/test_engine_late_usage.py --junitxml=/project/alex_phd/runs/rlm-research-r4/analyses/core-harness-review-2026-09-09/INDEPENDENT_REVIEW_TESTS.xml
```

An independent CPU matrix with seed731 compared the base `git show` observation module against the changed module across80 stdout/stderr/display cases, with escaped characters, emoji, empty channels, optional typed fault/exception, and budgets512–1065. All80 no-executor-loss encodings were byte-equivalent under sorted strict JSON. Adding17 executor omissions per channel gave exact `17 + source_length − delivered_length` totals in all80 cases, no double count, no structural rejection and no budget overflow. `git diff --check` also passed.

Boundaries: the observation loss accounting concerns the existing observation candidate fields plus recorded executor truncations; it does not newly expose deliberately excluded source fields such as retained traceback text. Existing behavior for those fields is preserved, as required by no-loss compatibility. The 512-character floor is qualified for the concrete built-in identities/count ranges in the tests, not arbitrary oversized structural metadata. The review does not add broad hardening requirements or apply these Responses-core changes to the separate frozen Prime/nano campaign runtime.

Reviewed hashes:

| File | SHA256 |
| --- | --- |
| `src/rlm/engine.py` | `e994c5edbafca91e847f201542262513151b31b08d81555326664cf8f3f2079a` |
| `src/rlm/observation.py` | `26591f9ab995a11bbb956adf4254d8e65414ed761d245cd4b889850575dbf80f` |
| `tests/test_observation.py` | `5e569d5f6e08dcf1973bc40aea15101ab314e834762c512ba76532880110c432` |
| `tests/test_engine_late_usage.py` | `6ac05044a6e759bcfca7ce94f37f6a1efbfe1f715681e039969d1ab2e8f4452b` |
