# Bounded AG native/HF one-step implementation

Goal: implement the approved proposal
`ideas/2026-09-12-agnews-native-hf-one-update.md` (SHA
`0ea086c77c74be35ce59a889324d07016e91bc296ef7911998e2c44c5c7f021d`).

1. New input/study, native collector, CPU mask handoff, single-load numeric trainer
   and owner; two focused real fixtures. Reuse sealed standard AG builder, V4
   native lifecycle, token decoder, exact masks/logprobs/importance/RLOO/loss.
2. Add conditional updated AG256 evaluator reusing the sealed V2 baseline schema;
   retain existing c32 evaluator. Seal full closure, QUESTION.yaml/MD, evidence and
   commands for MAIN review/launch. No GPU launch from this agent.

No old source/output edits, install, heldout training/selection, retries, hidden
renormalization or probability-gate changes. Native128 calls=32 fixed B4 prompts
x4 actions, T.5; count RLOO/128, fresh c32/fresh AdamW/one step. Owner1100,
external1200; native650/CPU masks60/HF350 plus40 cleanup reserve. Per-call raw
checkpoint and complete step receipt; every failure stops without an update.

Preparation target25–35 minutes, stop/defer if import work grows beyond that bound.
