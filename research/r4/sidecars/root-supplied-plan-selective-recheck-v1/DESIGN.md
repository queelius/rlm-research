---
id: root-supplied-plan-selective-recheck-v1
status: cpu_prepared_no_gpu
date: 2026-09-10
planned_calls: 24
---

# Confidence versus uniform c32 recheck

Use the exact adopted supplied-plan40 c32 maps as an unchanged baseline. Within each of its eight
episodes, select 25% of IDs either by lowest exact label-token mean log probability or by a fixed
label-blind uniform hash. Repack selected records in original episode order into one 16-record call
at size64 or two 32-record calls at size256. Both arms use the same c32 binding, prompt contract,
sampling parameters, and paired fresh seeds. Prior labels and gold are never rendered.

Only a native-authenticated complete recheck batch can update selected IDs, and every returned label
then overwrites its old value unconditionally. Any unavailable batch makes the episode NULL; any
authenticated-invalid batch makes it observed invalid. There is no runtime fallback, partial salvage,
retry, or reroll. The unchanged baseline remains a separate comparator.

The public deterministic J1 reducer scores a valid merged map. Private gold is analysis-only. Report
selected error capture, correction/regression, full-map accuracy, J1 exact/absolute error, confidence
versus uniform paired changes, natural overlap, availability, and incremental plus shared-baseline
physical costs. Four clusters recur at nested sizes64/256 and are research/optimizer exposed.

One A100, at most four workers, 1,800 seconds outer cap, no training/checkpoint/root calls. MAIN alone
may launch after reviewing READY and the prospective audit method.
