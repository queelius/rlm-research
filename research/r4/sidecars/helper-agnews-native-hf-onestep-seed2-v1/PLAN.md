# Bounded AG native/HF one-step seed replica

Goal: mechanically reuse the already qualified one-step implementation while
freezing a second native/HF seed schedule and new output identity.

1. Copy the qualified source additively; change only native seeds, HF seed,
   coordinate IDs, output identity and replica metadata. Exercise the seed delta,
   native request/decoder, and real tiny HF update fixtures.
2. Add conditional updated AG256 evaluator reusing the sealed V2 baseline schema;
   retain existing c32 evaluator. Seal full closure, QUESTION.yaml/MD, evidence and
   commands for MAIN review/launch. No GPU launch from this agent.

No old source/output edits, install, heldout training/selection, retries, hidden
renormalization or probability-gate changes. Native128 calls=32 fixed B4 prompts
x4 actions, T.5; count RLOO/128, fresh c32/fresh AdamW/one step. Owner1100,
external1200; native650/CPU masks60/HF350 plus40 cleanup reserve. Per-call raw
checkpoint and complete step receipt; every failure stops without an update.

Preparation is a bounded mechanical reuse of the qualified parent, not a new harness.
