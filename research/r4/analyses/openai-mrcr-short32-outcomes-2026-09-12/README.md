# Short32 outcome audit

CPU-only, write-once analysis of the already admitted short32 base calibration. It independently
checks the sealed V2 closure, exact 32-coordinate inventory, episode digests, native start/result
pairs, token-level native-to-trace causal mappings, root/child roles, official reward, exact and
near-exact retrieval, marker-bearing wrong answers, unavailable outcomes, usage, and tool evidence.

The watcher polls every 30 seconds for at most four hours with CUDA hidden. It writes only this new
analysis directory and does not query heldout records, invoke a model, retry episodes, or alter the
active sidecar.
