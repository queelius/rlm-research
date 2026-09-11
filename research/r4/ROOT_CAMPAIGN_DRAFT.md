# Draft: eight fresh-policy root-only RLVR rounds

2026-09-08. Design only: no implementation, launch, or modification of frozen pilot inputs. The single-step pilot establishes whether capture, correction and an actual update work; it is not an adequate learning campaign, and a null eight-episode validation difference would not establish that root learning is ineffective.

## Question and frozen campaign recipe

Can eight successive fresh-policy root updates improve reliable tool use, coverage and strict aggregation when child competence is held fixed? Recommend an independent campaign starting from the exact original converted root, rather than silently counting the pilot as round1. If continuing the pilot is chosen instead, explicitly rename the campaign as seven additional rounds and bind its original rollout generation, optimizer and checkpoint as round1.

Use the pilot's same four training contexts/eight HUM/NUM tasks;32 episodes per round (four seeds/task), maximum256 training episodes and eight actual updates. Fixed child throughout: `c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`. Initial root: `857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6`. Base manifest: `19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f`.

Keep native renderer, executable-example prompt, unconstrained generation, temperature .5, full support,2048 tokens/call, depth1, no compaction, strict terminal rewards and null infrastructure exclusions. No schema intervention from the concurrently running leaf ablation. Predeclare fresh training seeds as the first eight SHA256 hex digits of canonical JSON `["root-campaign-v1",981260600,round,task_id,repeat]`, modulo2^31−1; reject collisions against earlier campaign and pilot seeds before freezing. Validation seeds are fixed across checkpoints and excluded from training seeds.

Retain LR5e−5, BF16 frozen base/FP32 rank8 root LoRA, AdamW weight decay0, clip1, TIS cap2 and unchanged v2 distribution guards. Recommend **persistent Adam moments across rounds**, constant LR, and one global optimizer-step increment per successful round. This requires a small additive trainer change: restore optimizer moments, require their previous step r−1, then save step r. Restarting Adam each round is a simpler alternative but a different optimizer recipe, not something to happen implicitly because the pilot helper constructs Adam internally.

## Round state and validation schedule

`checkpoint r−1 → immutable serving binding → fresh32 captures → authenticated root-only group → one update → checkpoint r → next serving binding`.

Each round uses its own directory and round manifest binding campaign/source hashes, previous checkpoint/config/optimizer hashes, fixed child hash, seed/coordinate plan, actual native requests, runtime image/service identity, export group hash and resulting checkpoint. The rollout root and training-start root must be exactly the same checkpoint on disk. Serving retains its recorded common BF16 LoRA inference cast; HF training retains FP32 adapters and the same distributional correction guards.

Capture every outcome; select only nonempty valid root-action episodes in within-task mixed binary-reward groups. Child actions are evidence, never targets; prior root actions and child/tool observations are masked context. Preserve actual aliases and physical native token prefixes/logprobs. One full-batch gradient accumulation precedes the sole optimizer step. Consequently `HF_old = current.detach()` is valid **within that fresh generation only**, despite carrying Adam state. No stale group reuse, multiple epochs, extra optimizer steps, or assertion that conditional TIS is exact trajectory importance correction.

Run the same root-validation8 before training and after rounds2,4,6,8:40 validation episodes total, all with the fixed child. Reuse the just-loaded service for validation, then begin the next fresh rollout collection; no separate service cycle is needed. Save every checkpoint regardless of validation. Select among checkpoints0,2,4,6,8 by strict validation successes, earliest checkpoint on ties; also report the final round8 result separately. No LR/seed/prompt changes or performance-based early stopping inside this campaign. Eight repeated validation coordinates are development measurements on two contexts, not independent evidence of generalization.

Stop and retain artifacts on identity/mask/guard failures, no mixed group, OOM/time cap, missing checkpoint, or exhausted campaign budget. Do not refill a no-mixed round with endless seeds or relabel failures as negatives. Restart only incomplete orchestration, never repeat a completed optimizer step: a retained valid checkpoint advances the cursor even if later analysis failed. Interrupted pre-step attempts may be diagnosed, but any retry gets a new attempt identity and its provenance recorded. Report actual rounds completed rather than claiming eight updates when fewer occurred.

## Minimal additive reuse boundaries

| Boundary | Reuse | Narrow generalization needed |
|---|---|---|
| Round binding/serving | Existing dual-LoRA service launcher and endpoint descriptors | Replace root alias/path/hash per round; child remains fixed; authenticate `/models`, config and raw audit model identities |
| Native capture/export | Pilot trusted depth routing, native wire capture, `episode_turns`, mixed-group math | Accept a frozen round spec instead of hardcoded original40/spec SHA; require32 training episodes and current-root binding; validation stays a separate nontraining export |
| Trainer | Pilot masking, tensor audit, TIS math, guards, checkpoint capture | Read authenticated round-start adapter and prior optimizer; increment global cursor; do not invoke the old original-only provenance guard or monkeypatch frozen files |
| Coordinator | Existing bounded collection/checkpoint conventions | Small explicit state machine and append-only round manifests; no generic experiment framework |

Keep the current563-line pilot trainer frozen. Its original-root/40-episode/hash checks are deliberate and cannot be bypassed for later rounds. New campaign code must preserve those checks parametrically under an immutable round manifest. Focused qualification should catch stale root bindings, child credit, reused generations, wrong optimizer continuation and crash-after-step double updates; one tiny two-generation PEFT CPU proof is enough before the first campaign launch. No broad repository suite is proposed.

## One-A100 execution and expected cost

Recommend serial inference/training phases with full inference-process stop/start. The current inference allocation was33,248MiB of40,960MiB at inspection; co-resident training is not budgeted. Service startup measured70.28 seconds from existing SERVER_START/READY artifacts. Sleep/offload or hot weight reload could save restart cost but adds an unqualified lifecycle and is not required for eight rounds.

At inspection,38 pilot episode records accounted for2,123.98 aggregate episode-seconds (mean55.9 seconds), with two still outstanding and other jobs sharing inference. Four-worker ideal throughput would put32 episodes near7.5 minutes; long tails and changing root behavior make this only a planning estimate. Budget roughly8–15 minutes collection,1–5 minutes optimization, and1–2 minutes service transition per round; actual trainer time/memory must replace these guesses after the pilot. Eight rounds therefore suggest80–176 minutes, plus roughly10–20 minutes for validation and15–30 minutes for later transfer: **about2–4 A100-hours**, not a measured guarantee.

Use a four-hour campaign envelope including validation, transfer and transitions; per-round collection cap1800s, training load+optimization cap600s, service-ready cap180s, validation8 cap600s, transfer48 cap1800s. Their individual maxima exceed the global budget, so the global deadline wins and records an incomplete campaign. Do not start a new round when fewer than15 minutes remain. Allow an already completed optimizer step to finish immediate checkpoint serialization. Keep other ready jobs queued for after the campaign, not concurrently on the same40GB allocation.

## Later transfer and interpretation

Before round1, freeze six new64-record root-held-out contexts from unused official source-training question groups, disjoint from all pilot root train/validation groups and prior composition groups. These questions remain leaf-SFT-supported: this tests root transfer, not unseen leaf knowledge. Evaluate original root versus validation-selected campaign root with the same fixed child on12 queries×2 seeds×2 arms=48 paired episodes **after** checkpoint selection. Existing previously inspected composition48 can remain a secondary report-only comparison, not a fresh blind test. A genuinely unseen leaf/source-family evaluation is a separate subsequent acquisition/design.

Report strict successes, coverage/recursion/tool failures, credited token counts, reward diversity, per-round guards and update magnitude, wall time and memory; distinguish format/process improvements from semantic errors.256 repeated training episodes over four contexts are a bounded mechanism study, not broad root generalization. A promising curve warrants a second independent campaign seed and new root contexts; plateau or missing reward diversity motivates a separately frozen task/reward/harness change, not an unrecorded mid-campaign intervention.
