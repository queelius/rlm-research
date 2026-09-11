# Isolated core evidence-fidelity fixes

Worktree: `/project/alex_phd/repos/rlm/.worktrees/core-evidence-fidelity-20260909`.
Branch: `fix/core-evidence-fidelity-20260909`. No commit or merge. Original REPORT/AUDIT and main source remain unchanged; all original reviewed main-source hashes were reverified after implementation.

Only four worktree files changed:

- `src/rlm/observation.py`: preserve executor-origin omissions in `truncation.executor_fields`; `truncation.fields` and `omitted_chars` report combined totals. Additional observation-stage loss is combined minus executor loss per field, so no loss is counted twice. No executor loss means unchanged encoding.
- `src/rlm/engine.py`: on a post-response run/action deadline failure, account valid response usage and re-raise the original deadline. Malformed envelope/usage and token-limit failures cannot replace the original deadline; the late answer is never accepted. Normal response handling is unchanged; no ledger API change.
- `tests/test_observation.py`: five added checks cover executor-only loss (including a fully dropped channel), combined-stage loss, unchanged no-executor encoding, all four channels plus a typed fault within the 512-character budget, and the real engine's next controller request using actual bounded capture and a fake environment.
- `tests/test_engine_late_usage.py`: twelve fake-clock cases cover run/action/both deadlines crossed with valid responses, token-limit overflow, malformed envelope, and malformed usage. Both-deadline cases retain action-timeout precedence. Valid usage is counted exactly once and deadline failure is traced.

Test-driven evidence:

1. `FIX_RED.xml`: 17 tests, eight expected failures before production changes (two missing-truncation failures; six known-token failures), nine passes including existing behavior/precedence controls.
2. `FIX_GREEN.xml`: initial three-map representation, 36 passing focused tests.
3. `FIX_BOUNDARY_RED.xml`: additional all-channel/fault boundary exposed excessive redundant metadata in that intermediate representation. Parent approved combined totals plus executor map, deriving observation loss by subtraction.
4. `FIX_COMPACT_GREEN.xml`: compact representation, 37 passes.
5. `FIX_FINAL_GREEN.xml`: final integration qualification, **38 passes** across observation, ledger, and fake-clock late-response files. Ruff check and formatting pass on all four changed files; `git diff --check` passes.

Final test command (workdir is the worktree):

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/project/alex_phd/repos/rlm/.worktrees/core-evidence-fidelity-20260909/src /project/alex_phd/envs/rlm/bin/python -m pytest -q -p no:cacheprovider tests/test_observation.py tests/test_ledger.py tests/test_engine_late_usage.py --junitxml=/project/alex_phd/runs/rlm-research-r4/analyses/core-harness-review-2026-09-09/FIX_FINAL_GREEN.xml
```

The 512-character test uses all four real channel identities, 100,000 omissions per channel, and a ValueError execution fault. It is a concrete supported-floor qualification, not a guarantee for arbitrarily large structural identities/count representations. The existing encoder still raises rather than silently dropping structural metadata if an envelope cannot fit. No limits were widened. No GPU/network call or generated-code execution was used; all controller code strings in the integration fixture remain opaque.

Final worktree SHA256:

| File | SHA256 |
|---|---|
| src/rlm/engine.py | e994c5edbafca91e847f201542262513151b31b08d81555326664cf8f3f2079a |
| src/rlm/observation.py | 26591f9ab995a11bbb956adf4254d8e65414ed761d245cd4b889850575dbf80f |
| tests/test_observation.py | 5e569d5f6e08dcf1973bc40aea15101ab314e834762c512ba76532880110c432 |
| tests/test_engine_late_usage.py | 6ac05044a6e759bcfca7ce94f37f6a1efbfe1f715681e039969d1ab2e8f4452b |

These changes do not alter any frozen Prime/nano experiment runtime or invalidate its recorded scores. Parent owns independent review and any eventual integration.
