# Bounded CPU-only audits

1. Exercise the sealed fresh512 evaluator's exact inner per-step qualification on committed RL step1, without changing its full8 endpoint gate. Then watch each complete RL step (30-second polling, four-hour maximum), authenticate source/action/parent/optimizer lineage and write immutable compact step JSON plus cumulative CSV/Markdown snapshots. Training-only rewards and costs are diagnostics, never heldout selection.
2. Watch the eventual fresh512 terminal arms, invoking the sealed raw decoder/comparator. MAIN's write-once fixed-endpoint receipt controls which completed trained arms are compared. If RL aborts, retain that aborted training status and compare only the authorized SFT/c32 endpoints; do not score an untrained RL endpoint as missing or wrong.

New analysis-local files only: gate_probe.py, audit.py, test_fixture.py, readiness/evidence and append-only results. No GPU, trainer/collector edits, model inference, parameter selection or automatic retries. Source-to-raw audit is not independently authored trainer replication.
