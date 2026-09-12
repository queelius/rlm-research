# Independent targeted-count audit

CPU-only, separate from the immutable live collector. `audit.py` imports no collector, validator, metric implementation or model-training code. It checks the approved READY and all226 source pins; restores each actual wire request/schema; decodes actual response token IDs through the pinned local tokenizer; checks IDs, finish, labels, physical token inventories and hashes; and recomputes all80 paired count tasks from host gold. Dataset totals, confusion and the prospective screen are checked against the owner output. Costs charge each full map once, with uniform-single-target and all-target views separated.

Run after OWNER_TERMINAL exists:

```sh
CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/analyses/helper-targeted-counts-local-review-2026-09-12/audit.py
```

Before completion it returns `AWAITING_TERMINAL` (exit2), writes no report and does not poll. Successful audit writes REPORT.json once; existing reports are preserved. A failed assertion is an audit discrepancy, not negative model evidence. One focused independently hand-scored fixture checks binary confusion, exact counts and missing maps. No GPU access or source mutation is authorized.

Interpretation remains dataset-specific: eight blocks per dataset yield48 TREC and32 news target tasks, all related through16 reusable full maps. The approved screen requires exact-count improvement, lower summed absolute count error, no macro balanced-accuracy loss and ≤1.25 uniform-single-target token ratio, with complete availability and qualified runtime. Its pass is a lead for independent root-count testing, not established benefit. Do not pool this run with previous full-label or flag-off counts. MAIN's separate size audit found TREC117/119/120 but news115/112/109 at sizes16/4/1: splitting is not monotonic across datasets, and this target-output treatment must establish its own paired evidence.
