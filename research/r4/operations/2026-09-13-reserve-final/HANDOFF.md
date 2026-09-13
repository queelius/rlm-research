# Final consolidation under the account reserve

Authority: September 13 user requests preserving 10% of the shared account;
14% was reported initially and the supported quota endpoint returned 13% at
18:55 UTC. This overrides earlier permission to spend the reserve. Do not start
another research branch or consume the reserve automatically.

The final admitted job is `b05-vector-credit-held72-seed2-v1`: 72 calls on the
same twelve held problems and three fixed models, with new paired sampling
seeds 202609520000 through 202609520023. No optimizer or checkpoint selection.
MAIN owns the launch under the coordinator flock, with science/owner/external
caps of 600/700/800 seconds. Terminal receipts determine whether it released.

The paired trained adapters and optimizer/RNG checkpoints are at:

- `sidecars/b05-vector-credit-local-v3/outputs/attempt-001/checkpoint-0001/`
- `sidecars/b05-vector-credit-joint-v3/outputs/attempt-001/checkpoint-0001/`

All relative paths are beneath `/project/alex_phd/runs/rlm-research-r4`.
Do not relocate or remove these or the base-model research cache. Public GitHub
snapshots contain compact source and analysis, not model weights or raw runs.

Read the final entries in `SESSION_CHECKPOINT.md`, `analyses/NOW.md`, and
`RESEARCH_QUEUE.md` before resuming. The plain-language synthesis is in the RLM
repository at `docs/research-checkpoints/2026-09-13-decision-interfaces-and-record-grouping.md`.

Ranked future work, requiring a renewed budget decision:

1. Test the fixed small-helper advantage on a different task where model
   judgment adds value; retain a deterministic baseline for explicit rules.
2. Compare a small helper budget with simple position/random controls. Native
   chosen-token confidence did not outperform those controls in the replication.
3. For RL, obtain varied decisions on consistently wrong candidates before
   increasing update count. Keep fresh held inputs and sampling repeats separate.

Do not treat proposed follow-ups as ready or authorized to consume the reserve.
