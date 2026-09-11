# Independent original-start root-RLVR seed replication

Recipe/design proposal is
`../../operations/2026-09-09-proceed/ROOT_SEED_REPLICATION_BRIEF.md`.
The new seed is981265001. All eight32-episode generations are fresh, starting
from original root857a7ce6 with empty Adam/RNG state; no inherited step3 or raw
rollout is admitted. Exact original task compositions and source splits remain;
every rollout seed is new. Python/torch/CUDA initialization uses the new seed,
then each new checkpoint restores its own predecessor Adam/RNG only.

The fixed c32de child, reward/admission, native likelihood capture, exact root
action masks, TIS loss, optimizer and checkpoint selection are unchanged.
The narrow authenticated unsampled-child HTTP400 overflow exclusion is used
from generation1 onward. Unknown integrity failures stop. Unanswered and
failed episodes remain separate nulls. No recovered root negative is admitted.

Small namespace entrypoints privately import pinned original coordinator,
trainer, lifecycleV2 and continuation exclusion sources. Their files are
unchanged. The native request bodies are generated only after each preceding
policy exists; immutable task coordinates/seeds and first-step source identity
are frozen now. No old likelihood or synthetic mask is substituted.

Validation8 repeats at steps0,2,4,6,8; earliest highest strict-success count
selects a checkpoint, with final8 also retained. The24 original/selected transfer
pairs use identical task/seed/dispatch order. Original then selected stage order
is inherited and remains a serving-order limitation. The exposed source contexts
provide exploratory replication, not independent confirmation. Training256,
validation40, transfer48 episodes total344; no additional replay is implicit.

Work cap5880 seconds and inclusive hard cap6000 seconds provide120 seconds for
cleanup. All original stage/per-episode limits and8-way concurrency remain.
Services and training are serialized by the existing coordinator; checkpoint
adapter/config/Adam/RNG/state are persisted each update. No hidden retries or
continuation from source checkpoints. The qualified lifecycle targets only its
authenticated processes. Main owns launch acceptance and allocation selection.

Preparation uses existing native/training environments with CUDA hidden. It
requires actual native task reconstruction and focused CPU checks. READY.json
is the campaign identity bootstrap; launch additionally requires successful
QUALIFIED_READY.json. Dynamic fresh-group training authentication remains a
first-rollout dependency and cannot be established using fabricated actions.
