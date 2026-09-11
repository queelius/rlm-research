# READY V3 authentication amendment

Final pre-launch review found that V2 pinned the reused QS replication `READY.json` but did not invoke
that package's verifier recursively. `study.verify()` now calls the qualified replication verifier
before checking this sidecar's own seal. A focused regression test proves the call occurs. This additive
V3 seal supersedes V2. Inputs, selected groups, prompts, seeds, conditions, bindings, budgets, and
outcomes are unchanged; no GPU call occurred.

