---
date: 2026-09-10
status: proposed_for_main_review
study: root-question-sensitive-terminal-rlvr-lr1e5-v1
implementation_authorized: false
gpu_launch_authority: MAIN_only
---

# Exact LR-only composed-task RLVR ablation

## Question and intervention

Does reducing AdamW learning rate from `5e-5` to `1e-5` make the very-small
question-sensitive composed-task RLVR intervention more stable or useful? This is a
matched one-factor ablation, not a reproduction of Steno (2026) and not a continuation
of the live high-LR policy.

Start independently from the exact QS recovery SFT6 adapter at
`root-question-sensitive-sft-recovery-v1/outputs/attempt-003/training/checkpoint-0006`:

- root adapter SHA-256
  `4d8287537a9ff3d8e33bc0314f64315dee06e71b801257b389dab8b667e27aca`;
- adapter config SHA-256
  `5bb10e33566ed74c56438c465a8c26fd6a5bd8f41f221ab0bf28517375607a76`;
- source state SHA-256
  `4c2fab6360030ee446e681f76e61591ac2892aad9c509332a244a12a05ddb68a`;
- fixed inference-only child SHA-256
  `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`.

Use fresh AdamW at RL cursor zero. Never load SFT optimizer state or any checkpoint,
moment, RNG state, or adapter from the high-LR RL campaign. Change only
`learning_rate: 1e-5`; preserve rank8, weight decay zero, norm clip 1, PPO clip 0.2,
TIS cap 2, temperature 0.5, within-task population-standardized advantages,
root-action-only masks, fixed c32 child, terminal 0/1 reward, admission rules, and
no-refill semantics.

## Fixed training data and exposure

Use the exact eight ordered windows in the existing `PLANS.json`: eight TRAIN contexts,
six composed task groups per context, and four samples per exact task. This is 24 planned
physical attempts per window and 192 total. Preserve every coordinate, seed, request
body, prompt, host-gold binding, group membership, and record order. A complete window
is consumed once; incomplete collection or a homogeneous/no-admitted group is a recorded
noop, never rerolled or filled. At most eight actual optimizer updates are possible.

The immutable parent scientific input hashes are:

- `PLANS.json`:
  `28445777e8d6249ffb9368356ca7ae3d1f2d61bc8b09b05a2b6ebb0abf3001e1`;
- `GROUPS.json`:
  `a1ecbc8df62d620b7a5e34bdf66db7f98b7b1557cd7682e6020208a32dba10d7`;
- `PUBLIC.json`:
  `29f450e2a301785c8b9d5bc23f7f5466c136d84e39aa93a4725991f138050773`;
- `HOST_GOLD.json`:
  `553553c65d19bf43e0cca9428f4f8949e8cfe8d25af9e1432c8945d06548c219`;
- `NATIVE_TEMPLATE.json`:
  `a4224b1363d1c2c9a49d9f9893c42516f4d4c4dc8abbd2f5653cff144a876293`;
- `PROMPTS_ACCURATE.json`:
  `bf14a8781a2efbfbea9dbde9dd7f644ea34d3a94cf89b1ea483439ea4ab20c7a`;
- `PROVENANCE.json`:
  `f6d701c31393d9f82d84ad4e139f4912a9708d53d41dc679b0d6759cd571151c`.

These files may be materialized byte-for-byte in the new sidecar and pinned to both the
new path and the parent path. `TASKS.json` is the exception: it must be regenerated under
the new campaign namespace because native `task_hash` and policy/generation bindings are
identity-bearing. A receipt must prove that all scientific fields and serialized provider
request contents remain byte-equal to the recovery-v2 source while enumerating the exact
namespace/hash fields that necessarily differ. Do not label the new recipe or generations
as the original campaign. Each new coordinate retains its parent source coordinate ID,
parent plan SHA, parent campaign generation identifier, and new campaign/generation ID.

## Namespace and dependency closure

Prepare only in a new sidecar
`sidecars/root-question-sensitive-terminal-rlvr-lr1e5-v1`, with outputs restricted to
`outputs/attempt-001`. Use a new campaign ID derived from the complete new recipe,
scientific input pins, start/child pins, and fixed schedule. Refuse an existing output
directory. The new CAMPAIGN must separately pin:

1. immutable parent scientific artifacts and their source paths;
2. regenerated native task identities and an old-to-new task-hash map;
3. the new `1e-5` recipe and trainer source;
4. every qualified collector/exporter/native/lifecycle/service dependency actually loaded;
5. the exact local model manifest, Python environments, and launcher/wrapper chain.

Avoid post-context alias imports: entry points must be executable in fresh CLI subprocesses,
and any function-local import must resolve to the new module namespace. Qualification must
exercise `env.run_slot` through the first fake provider transport request, native replay,
one group4 export, trainer preflight, and owner launcher argv/lifecycle registration. No
GPU model execution is part of preparation.

## Optimizer restore contract

The qualified trainer creates AdamW from the current recipe before restoring state.
PyTorch `optimizer.load_state_dict` restores saved parameter-group hyperparameters as
well as moments, so a source campaign checkpoint could silently reintroduce `5e-5` if
namespace authentication were weakened. The new trainer contract must make that impossible:

1. Step zero accepts only the pinned QS6 adapter with `optimizer_sha256=null`,
   `rng_sha256=null`, an empty Adam state, and every trainable parameter group at exactly
   `lr=1e-5`, `weight_decay=0`.
2. Step greater than zero accepts only a previous policy path below this new attempt's
   immediately preceding window. Authenticate adapter, state, optimizer, RNG, generation,
   parameter order, campaign ID, and actual cursor before deserialization.
3. Capture expected optimizer group fields before `load_state_dict`; require them to be
   identical after load. Add an explicit post-load assertion that every group retains
   `lr=1e-5` and the pinned AdamW hyperparameters before forward/backward.
4. After `optimizer.step`, require a one-step cursor increment and serialize adapter,
   optimizer, RNG, correction capture, parameter names, optimizer-group hyperparameters,
   runtime versions, memory, and hashes atomically in the checkpoint state.
5. Before starting the next window, independently reload the just-committed state on CPU
   and verify optimizer cursor, parameter-group LR, moment tensor inventory, RNG hashes,
   and checkpoint policy identity. A mismatch stops the campaign; it never falls back to
   fresh Adam or changes LR.

Focused tests must demonstrate rejection of a real or fixture `5e-5` optimizer state,
foreign high-LR checkpoint path, missing moments, reordered parameters, stale generation,
wrong cursor, and post-load LR replacement. A positive two-step fixture must retain
`1e-5`, Adam moments, and RNG continuity across a separate trainer process.

## Time envelope and checkpoint policy

Allow up to 12,000 seconds for the training phase, rather than silently inheriting the
prior 4,500-second envelope. Preserve a per-optimizer subprocess cap of 1,800 seconds;
collection retains its qualified per-window cap and the owner advances through the fixed
schedule until the 12,000-second training boundary. Reserve a separate 2,700 seconds for
the sole new fixed-last readout, plus 270 seconds for cleanup and a 30-second parent
termination margin: 15,000 seconds inclusive, owner release by 14,970 seconds.

Every actual update commits an atomic window-local checkpoint. The evaluated policy is
the last actually committed checkpoint after the fixed eighth-window cursor, including
the QS6 start if there are zero updates. There is no best-checkpoint, validation, or
protected-outcome selection.

## Readout and comparison

Make only 72 new protected calls: the new fixed-last policy on the already frozen 72-task
panel. Reuse, without rerunning, the authenticated QS6 start endpoints from recovery-v2
attempt-003:

- parent campaign ID
  `ecb91caf15a5673d35808cf9c6542b562aff8463e41cfc00b1566702fe7c366b`;
- `readout-start/export/MANIFEST.json` SHA-256
  `81774d0e3807deb1b2991ee64c5092c665cf3e93e03255f24f0a3ff7b34a3bd4`;
- `readout-start/export/EPISODES.json` SHA-256
  `155773184de5db6c7f367d1a735966f45f9712ff43c1b8b70b255a67b167bd01`;
- manifest status: 72 planned, 72 recorded, complete.

The new readout must prove exact coordinate/seed/request equivalence to that baseline,
apart from policy identity and unavoidable call IDs. Report paired raw/native correctness,
availability with NULL bounds, task/context effects, all 192 planned training attempts,
admission/noops, actual updates, optimizer/mask diagnostics, and capture/optimizer/readout
cost separately. Authenticated malformed or empty finals are observed zero; missing,
unreturned, or unauthenticated results are NULL, never zero-filled.

The primary estimate is the paired new fixed-last minus reused QS6 start effect. Comparison
to the terminal high-LR fixed-last is secondary and valid only after that independent run
releases and is audited; no live result or checkpoint affects this design, schedule, or
selection. Success is evidence for a lower-LR continuation only if the fixed-last endpoint
improves without availability loss and the full optimizer provenance remains valid. A noop
or zero-update run is reported as no intervention, not as a trained-policy result.

## Alternatives not chosen

- Continuing from the high-LR RL checkpoint would confound LR with policy and optimizer
  history, so it is excluded.
- Changing rank to 64 would require a different adapter/start and is not a one-factor test.
- Adding thesis-inspired token-cost shaping could improve credit density but would confound
  the LR question. It remains a later offline-trace feasibility check if homogeneous groups,
  rather than optimization stability, dominate this run.

No implementation, READY seal, GPU service, or launch is authorized by this design.
