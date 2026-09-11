# Independent root seed: CPU preparation handoff

The original-start replicate is prepared in
`sidecars/root-rlvr-independent-seed-v1/`. The design brief was written and sent
before implementation at ROOT_SEED_REPLICATION_BRIEF.md. Seed981265001 changes
all288 unique rollout coordinates (256 training,8 fixed validation,24 paired
transfer), with no collision against the original campaign's seed set. Five
validation checkpoints and paired transfer make344 planned episode collections.
No new root96 outcomes were read. Frozen padding files were unchanged.

The initial policy is original857a7ce6 at step0; Adam, RNG and saved-state hashes
are null initially. All eight fresh32-episode generations must be collected.
No earlier checkpoint, episode, action logprob or mask is admitted. Python/
torch/CUDA are initialized with the new seed, and later updates restore only
this attempt's predecessors. Same c32de child, exact tasks/splits/context texts,
reward/optimizer/loss/guards, per-episode contract, checkpoint-every-update and
earliest-maximum validation selection remain. Source-derived adapters introduce
only namespace/seed, fresh coordinate order, bounded envelope and the already
qualified exclusion-only overflow provenance identity.

Three focused TDD tests failed on missing preparation, then passed. Native
preparation rebuilt identical actual prompt/context text and task membership.
Private campaign/lifecycle/exclusion imports authenticate successfully with the
original root/fixed-child binding. A real prior native three-call fixture gives
two credited root targets, zero child credit and zero observation credit. The
existing training environment verified an empty initial Adam and rejected child
and unmasked-observation mutations using its tiny CPU test fixture, without
creating training artifacts. The exact actual9972-token unsampled child-overflow
certificate remains excluded; a wrong-alias mutation is rejected. No broad suite,
GPU/model/service call, environment mutation, or parent acceptance occurred.

The campaign identity is
`a5132888b9e6700e7378e039335fa55b8ee6ebdc4ee7f8898351876ea123df62`.
CAMPAIGN.json SHA256 is
`fdb01b5516298d02439a7990a4cb098b994ed3c83c4ac81a1ed1e7b2d3a2c859`.
The bootstrap READY.json records initial freezing; launch additionally requires
QUALIFIED_READY.json, which pins all exact execution/admission/lifecycle sources
and contains the completed CPU evidence plus limits. DATA are the frozen inputs/
JSON files; RECIPE.json carries unchanged mathematical settings with the new seed
and5880-second work cap. AMENDMENT.json explicitly records zero inherited steps.
The inherited field name continuation_amendment_id is retained only for the
qualified exporter protocol; its new value binds this independent step0 study.

Exact proposed argv:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-independent-seed-v1/campaign.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-rlvr-independent-seed-v1/outputs/attempt-001
```

Main owns GPU assignment, actual allocation fit and launch acceptance. Inclusive
cap6000seconds reserves120seconds beyond the5880-second work budget. Actual
prior two envelopes summed5484.34seconds, including467.10seconds reported startup;
the new100-minute cap is a bounded exploratory allowance, not promised completion.
Source training Python is the existing original campaign environment; native
collection uses prime-rl-5990b1b. Neither environment changed. Every update retains
adapter/config/Adam/RNG/state and full failures; no automatic retry exists.

Dynamic endpoint preparation and first fresh-group likelihood/mask authentication
cannot be CPU-completed without actual collection. They retain the qualified
source checks and will fail observably at runtime if incompatible. Transfer
original/selected coordinate order and seeds match, but serial stage order remains
original then selected. There is no unchanged-policy replay or reversed stage
order control. Exact source contexts are exposed developmental data, so this is
exploratory independent-seed evidence, not confirmation. No new scheduler,
optimizer algorithm, core exporter refactor or manufactured likelihood was used.
