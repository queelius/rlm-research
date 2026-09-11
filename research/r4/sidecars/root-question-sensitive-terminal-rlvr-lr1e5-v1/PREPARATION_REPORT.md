---
date: 2026-09-10
status: cpu_prepared_pending_main_review
campaign_identity: 9b59a77098cc4c289237967f9154eb2a5423cbbda4e69889f4da1e47741c4961
campaign_sha256: c5fff6a7cc4512c4e8e55fcdf910b5e90f7e871e87cb03aec2d60489cb1fd597
gpu_calls: 0
---

# LR1e-5 preparation report

The isolated producer is CPU-prepared but deliberately unsealed: `READY.json` and
`outputs/attempt-001` are absent. The fixed scientific inputs are byte-equal to recovery-v2 except
native `task_hash`: a real `make_task` check proved prompt and 1,079-token first-prefix equality
while the hash changed with the new study identity. All other TASKS fields remain equal, and the
source map records every old/new hash.

The recipe SHA-256 is
`721be0695105a5beffed0301c91a29bbaa13c5e09c58d237bbb31d574a6022ad`.
Relative to the recovery-v2 recipe, only schema, LR (`5e-5` to `1e-5`), and per-optimizer cap
(`240` to `1800` seconds) differ. All training coordinates, seeds, ordering, rank8 adapter, c32
child, objective, masks, reward, TIS/PPO settings, and no-refill behavior remain fixed.

The trainer asserts LR1e-5 both before and after `optimizer.load_state_dict`, rejects foreign
high-LR policy paths, preserves noops between the last commit and current fixed window, and records
optimizer group hyperparameters with adapter/Adam/RNG state. The implementation uses the qualified
sparse credited-position likelihood head, whereas the original high-LR first update used dense
logits; it is objective-matched but not bitwise one-factor equivalent.

A failed first transport qualification using copied parent task hashes is retained under
`qualification-transport1-failed-source-task-hash/`. After deterministic namespace-local task-hash
generation, the actual one-slot `env.run_slot` fixture reached the fake native provider once,
returned one authenticated result, and preserved the expected 1,079-token prefix in 18.37 seconds.
A real tiny CPU Torch AdamW fixture restored step 1 at LR1e-5, advanced to step 2, and rejected a
saved LR5e-5 parameter group through the actual `lr_train.restore_optimizer` path. Both made zero
GPU calls.

The sole new protected readout is fixed-last72. The complete authenticated QS6 start72 is reused
from recovery-v2 attempt-003 without new calls. Later reporting requires raw/native accuracy plus
agent-reviewed faithful+strict execution and forbids gold-zero coincidence promotion or NULL
zero-filling.

Focused verification: `10 passed in 0.63s`; fresh native/training CLI namespace probes passed,
`lr_owner.py --help` returned zero, campaign pin verification returned the identity above, and no
GPU/service calls occurred. Superseded pre-review campaign revisions are retained under
`superseded/`.

The owner may terminate before consuming window 8 because of the resource boundary or a training
error and still complete its sole readout. Such a result must be labelled by completed-window cursor
and actual optimizer step; readout completion alone is not full-eight completion. The inherited
producer cost ledger is non-authoritative for native physical counts, so the independent raw
role-audit recount remains required.
