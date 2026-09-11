---
id: root-operator-dose-intermediate-readout-v1-ready-v2-correction
date: 2026-09-10
status: additive-prelaunch-correction
---

# READY V2 correction

Independent post-seal review found two implementation defects before acceptance or launch. V1 could
allow cleanup until the phase boundary rather than at most 30 seconds, and its cost ledger covered
only free-path physical records. V2 changes only the owner: cleanup is bounded by the earliest of
`now + 30`, the fixed phase end, and the owned deadline; the ledger separately inventories all free
and probe traffic, response authentication, returned completions, known/unknown usage, and retained
record hashes. Missing-result usage is never synthesized.

The V1 READY and sources remain unchanged as rejected pre-review history. Inputs, checkpoint order,
seeds, prompts, 64 free endpoints, 48 probes, metrics, and scientific caps are identical.
