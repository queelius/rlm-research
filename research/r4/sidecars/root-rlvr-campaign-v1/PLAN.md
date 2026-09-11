# Eight fresh-policy root-only rounds

Approved implementation decision: IMPLEMENTATION_DECISION.md; design: ../../ROOT_CAMPAIGN_DRAFT.md.

Goal: an independent eight-update root campaign with fixed selected child, persistent AdamW,
fresh immutable generation coordinates, and serial owned inference/training. A stopped campaign
reports the actual retained updates, never an invented eight-step curve.

Architecture: small local data/identity helpers, a parametric native collector/exporter using
qualified frozen helpers, a persistent-optimizer TIS trainer, and one explicit serial coordinator.
The immutable checkpoint commit is authoritative; the coordinator cursor is derived from commits.
The original hardcoded pilot collector/trainer verification is never weakened or called with fake
original provenance. CPU proof uses synthetic tiny PEFT generations, not research measurements.

Global constraints: new sidecar only; no GPU/service calls during preparation; original root
857a7ce6…, fixed child c32de129…; namespace root-rlvr-campaign-v1, seed981260800;
8×32 new training trajectories, validation8 at0/2/4/6/8, frozen transfer48; T.5 full support,
2048/call, exact root-only native physical-prefix action targets, no retokenization/truncation;
LR5e-5, wd0, clip1, cap2, existing guards, FP32 LoRA/BF16 base; one AdamW step per generation.
Four-hour global envelope; collection1800/train600/start180/validation600/transfer1800 seconds;
no new round below900 remaining seconds. No stale rollout reuse or automatic pre-step retries.

## Implementation and evidence

- [x] Freeze deterministic round/validation/transfer inputs and disjointness provenance.
- [x] Add explicit generation/checkpoint contracts; test stale generation and wrong optimizer.
- [x] Adapt qualified native capture/export parametrically; bind actual endpoint/weights/image.
- [x] Carry optimizer/RNG between exact root checkpoints; test two tiny fresh PEFT updates,
      child masking, and checkpoint recovery without a second update.
- [x] Implement bounded serial service lifecycle, resumable completed stages, validation selection,
      and paired original/selected transfer; stop with retained evidence on terminal failures.
- [x] Focused CPU verification and exact run/resume handoff. Source seal/READY are emitted last.

User's external-sidecar isolation and bounded research review take precedence over Git/worktree,
branch, broad-suite, or approval ceremony. No Git files or existing sidecar files are modified.
