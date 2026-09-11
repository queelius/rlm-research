# Question-sensitive SFT72: CPU implementation handoff

Prepared 2026-09-10 by bridge_audit (implementation author). CPU-only preparation is complete; no scientific attempt, GPU launch, service, lock, or queue mutation was performed. MAIN owns acceptance and launch.

## Executable seal

- Sidecar: `/project/alex_phd/runs/rlm-research-r4/sidecars/root-question-sensitive-sft-v1`.
- `READY.json` SHA256: `92b950f663dbf76b96a4ca0e9d2e5841bb72d269b6d256f383a4e6521235fc07`.
- Identity: `9af3b4f1589a173bae7be54a1266bf4aecdbada1d5a3c27b603e61131269ddfa`; 1,455 source pins and 4,434 input pins.
- `CPU_REPORT_v2.json` SHA256: `6fe17eab2f169f078fd27a58772478583976f9c7c6cb7afbba527a486806d714`.
- Final focused qualification: 15 tests passed in 134.88 seconds (two dependency deprecation warnings). The subsequent actual standalone owner `verify` exited 0 and returned the same identity.

Exact launch command:

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-question-sensitive-sft-v1/qs_owner.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-question-sensitive-sft-v1/outputs/attempt-001
```

The same interpreter and owner with `verify` perform the source/input verification. All sealed sidecar files are now immutable.

## Frozen experiment

The refreshed named actual/accepted-root inventory leaves 976 eligible groups. The first 320 hash-ranked groups were allocated once, without labels or gold-based reranking: eight training, four development, and eight protected contexts of 16 records. All records are TREC training/c32-training/prepared-catalog exposed; root-new is limited to the explicit named inventory, not global research or pretraining novelty.

Training is exactly 72 separate genuine c32 acquisitions followed by 216 authored current-root action targets. Targets use actual acquired predictions, with no gold repair or success filtering. Six predetermined full-corpus updates start from fixed24 weights with fresh Adam; this is not continuation of its old optimizer. Producer/reduction/terminal target mass is .45/.50/.05, learning rate 1e-4, and all prompt/history/child tokens are masked. Each update saves adapter, all 504 named Adam states, RNG, cursor, ordinal, and ancestry. Fixed6 is mandatory; missing fixed6 is a failed treatment, never a fixed5 substitute.

The contemporaneous unchanged/fixed6 evaluation inventory is 144 protected plus 16 development endpoints, without the procedural card. The development readout uses M1/M2 only: `EXECUTED_BASELINES.json` explicitly separates its eight tasks per policy from the 36 defined development specifications. Zero-answer floors are 32/72 training, 26/72 protected, and 3/8 executed development; these realizations are retained. `ANTI_COINCIDENCE.json` reports fixed alternative-operator baselines without selecting questions.

The prospective six-example gate is validity/cost only: finite role/nonliteral NLL, correct supported masks, measured prefix/memory/forward cost and retained protected-readout reserve. No loss-floor, fit, efficacy, or old four-of-six admission threshold applies. Every measured NLL, including near-zero values, is retained. GPU cost qualification has not yet occurred.

## Timing and accounting

Outer/work/owned caps are 8100/7920/8070 seconds. Inclusive stages reserve capture 1200, training 2100, unchanged evaluation 2100, and fixed6 evaluation 2100 seconds, plus 420 final work seconds. Each evaluation phase includes startup and release, with at most 150 development and 1950 protected seconds; unused development allowance does not secretly enlarge the protected cap. Qualified per-service release is 90 seconds, final owned cleanup 150, and outer margin 30.

All 160 evaluation slots are preinventoried. Missing RESULT remains native-final NULL with attempted/never-started/unfinished distinctions. The raw physical union includes capture, development, protected, and other request files, including failed requests and unknown usage; authored transport targets are separate. HTTP attempts are not all claimed GPU generations, and billing is unknown.

## Focused qualification scope and retained corrections

The new 744 Python lines are `qs_problem`, `qs_study`, `qs_protocol`, `qs_collect`, `qs_learning`, `qs_binding`, `qs_train`, `qs_owner`, preparation/sealing scripts, and four focused test files. `DESIGN.md`, `PLAN.md`, `APPROVAL.md`, and `RECIPE.json` specify the approved table, gate, and lifecycle. Qualified ancestor sources are pinned and unchanged.

Three authored native ACP/IPython fixtures exercise threshold, maximum, and conditional-sum acquisition, actual observations, three action targets, and supported loss masks. One actual captured teacher trajectory is expanded to 72 copies solely for the tiny CPU trainer-entry fixture; it runs six real CPU Adam updates with 504 trainable parameters and checks saved states/RNG/binding. This is not evidence of 72 independent acquisitions or GPU model fit. Actual owner-to-wrapper-to-intercepted inference entry, configured caps/two-LoRA routing, interruption, missing-fixed6 behavior, and raw request union are tested.

The first final qualification failed because its test used an unsorted request glob to identify the first root request; the actual collector had already authenticated that request. The fixture reader was corrected and all tests rerun. `qualification-final-001`, `CPU_REPORT.json`, and `QUALIFICATION_CORRECTION.md` preserve this history, including the clarification that an intended six-update constant in the failed report was not proof that those updates executed in that run. `CPU_REPORT_v2.json` is the fresh passing receipt. There was no superseded scientific attempt or READY.

Independent reviewer runtime_port has separately recomputed all 320 source records/selection and all 180 oracle truths without discrepancy (`analyses/root-question-sensitive-sft-cpu-2026-09-10/INPUT_CHECK.json`, SHA256 `22f594cab8a90251d781bc2cde659ef70455ba632f59de85c9db0b9b28ddcca6`). Its remaining review and MAIN acceptance are separate from this author handoff; no full independent pipeline acceptance is claimed here.
