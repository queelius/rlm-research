# QS72 capture-completion recovery

This is an infrastructure recovery of the frozen `root-question-sensitive-sft-v1` study, not a new scientific condition or an outcome-selected rerun. The original attempt remains immutable and failed its complete-corpus gate after a serial capture deadline. Its unchanged-policy 80-endpoint readout is the sole baseline and must finish before this owner starts.

## Fixed boundary and retry semantics

The post-capture inspection found indices 0–64 with authenticated `TEACHER.json` and `EPISODE.json`, four transport records each, and complete role/typed audit records. Index 65 has `FAILURE.json`, zero physical records, and zero role/typed records: the native environment began but no root or child request was dispatched. Indices 66–71 have no coordinate directory. The recovery therefore reuses indices 0–64 exactly once, retries index 65 with the same coordinate/seed and labels that retry `retry_after_pre_request_deadline_failure`, and makes the first attempt for 66–71. It never resamples a completed native response. All original artifact hashes and the actual scan timestamp are frozen in `inputs/RECOVERY_BOUNDARY.json`.

Capture stays serial. Seven missing trajectories are expected to need roughly two minutes at the observed rate, so changing the qualified native collector's concurrency would add a larger validity risk than useful time savings. The recovery collector is hard-coded to the original plan slice `[65:72]`; it cannot accept a replacement index or seed.

The combined corpus verifier authenticates each of 72 teachers, its exact coordinate, native prefix, three current-action turns, one episode-local genuine c32 child record, and unique child receipt. It pins all teacher, episode, and actual-child files. Sixty-five paths resolve under the original attempt and seven under the recovery attempt. No partial corpus or later best subset can train.

## Unchanged science

Starting root is the exact fixed24 adapter; child is the same c32 adapter. The original 72 tasks, public files, questions, labels, layouts, token masks, role weights, seed, six full-corpus passes, learning rate, fresh Adam0, gate coordinates, and fixed checkpoint6 selection are unchanged. The qualified trainer is called on the combined corpus without reward shaping, guide, repair, or gold filtering.

Only recovered fixed6 is evaluated: original dev8 plus protected72 and the same original seeds. The original unchanged dev8/protected72 artifacts are referenced and pinned, never recollected. The comparison remains phase-confounded and exploratory; recovery adds a different wall-clock/service phase and does not turn the panel into an independent replication.

## Budgets and accounting

Recovery cap is 5400 outer / 5370 owned / 5220 work seconds: capture 600, training 2100, one fixed6 readout 2100, finalization 420, cleanup reserve 150, outer margin 30. Startup is within each stage and release reserves 90 seconds. The run refuses to start if original actual elapsed plus the recovery cap would exceed the approved combined 10800 seconds.

The ledger separately unions original partial capture, original unchanged baseline, recovery missing capture, and recovery fixed6 readout transport files. It distinguishes physical request attempts, HTTP responses, choice-bearing completions, and unknown usage. Original failed work is charged; reused teachers and baseline calls are not counted twice. Billing is unknown.

