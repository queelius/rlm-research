# Runbook

MAIN alone accepts and launches this sidecar. Before launch, privately export a nonempty
`STRICT_RLM_CALIBRATION_API_KEY`, assign exactly one owned GPU in `CUDA_VISIBLE_DEVICES`, and run
the `verify_argv` then `launch_argv` from `READY.json`. The owner performs credential preflight
before creating output, launches the already qualified released-base wrapper, collects exactly 96
requests with four workers, and releases all owned descendants. There is no retry or output reroll.

The only authorized output is `outputs/attempt-001`. Preserve it whether successful or failed.
Never invoke model-authored tool calls or code during collection or analysis.

