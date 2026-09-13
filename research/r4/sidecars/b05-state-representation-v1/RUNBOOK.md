# State-representation screen runbook

This is a CPU-prepared, MAIN-admitted GPU job. Do not launch it from an agent.

After verifying `READY.json` and its complete closure, MAIN may run the exact `argv` recorded in
that file under the shared GPU allocation lock. The owner starts one released Qwen3-4B-Instruct-
2507 service and executes all 72 frozen calls: twelve public stages, two paired decode seeds, and
the raw, unresolved-grouped, and resolved views. All unavailable results remain unknown.

The unresolved view groups each candidate with every applicable public update and check row. It
does not apply changes, select the latest check, compute eligibility, filter candidates, or expose
host labels. Prompt wording and token length necessarily differ across views and are not matched.

