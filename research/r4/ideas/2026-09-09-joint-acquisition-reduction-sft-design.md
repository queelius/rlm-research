# Joint acquisition → live reduction → stop: bounded SFT proposal

2026-09-09. Design only; no implementation, GPU launch, service, lock, queue edit, or frozen-source change. Proposed new sidecar: `root-joint-state-reduction-sft-v1`. The author implemented the preceding SFT/runtime plumbing; the evidence below comes from the independent sealed audits, not an independent audit of my own implementation. MAIN owns acceptance and the GPU queue. Restart48 is already running; queue files lag MAIN's live launch updates.

## Recommendation and evidence

Run a small **coherent-trajectory, role-balanced SFT pilot**, conditionally on MAIN's review and the pending restart result. Do not extend the old epochs or simply mix their map-literal targets with producer targets.

Complete-demo training fell from unchanged 8/16 to 1/16 in both action-only and action-plus-terminal arms; adding an already nearly saturated terminal objective did not help. Original corrective free accuracy was 7/25 available, with seven NULLs among 32 planned, versus unchanged 10/32 and first-producer 2/32. Its lower CE did not produce faithful scalar reduction in free rollouts. The independent completion now finds corrective 5/14 available among 16 planned (operational 5/16; bounds 5–7/16), but only **one** actual map/user-scoped scalar reduction—the same count as unchanged. Four other successes followed fresh scoped child acquisition. No trained fresh-name corrective program appeared. Thus conditional answer improvement is not evidence that the intended corrective mechanism was learned.

The old 32 captures are reusable for a loss-coverage diagnostic: they contain 80 valid producer targets (8,362 tokens/pass), 32 corrective targets (9,259), and 32 authentic terminals (160). Eight explicit erroneous actions remain masked. However, old width-4 producers overwrite their current batch variable; correction reconstructs all maps from copied observed literals. Of corrective tokens, 5,787/pass are map payload and 1,664 are mechanism spans. Those are token counts, not gradient shares. Mixing those traces would test coverage without fixing the producer-to-live-state handoff.

## Preferred experiment: 16 new genuine trajectories

Reuse the **same eight training contexts/128 record groups**, selected without semantic correctness, and their two training query compositions. No evaluation rollout enters training. Select one width per context/query: eight width-16 and eight width-4, balanced within category and single/union scope rather than confounded with context parity. Freeze the 16-coordinate plan before capture.

Author and actually execute each complete trajectory in one native REPL:

1. A first productive action reads real `id`, `user`, `text` records, initializes a named accumulator, calls unchanged c32 on a real batch, validates the returned map, and updates/prints the accumulator.
2. Subsequent width-4 actions acquire the next batch and update that **same live accumulator**. Their native observations expose cumulative state. Never silently merge maps on the host or copy a complete map literal into the reduction target.
3. A reduction action uses the actual accumulator and actual records, filters IDs by the requested users, counts the requested category, and prints the scalar.
4. The authentic final is `Answer: N` from that returned scalar, with the real native final/EOS boundary.

Use four predeclared accumulator names, balanced across width/scope. The partial-state examples supervise continued acquisition; complete-state examples supervise reduction instead of another producer; scalar-observation examples supervise final/stop. Actual wrong child labels and consequent wrong dataset scalars remain unchanged. A transport or malformed-map capture failure is retained as a failed coordinate, not repaired or replaced; an incomplete corpus does not silently train a selected subset. No intentional error target is needed for this first pilot. Free roots remain free: no controller forces accumulation, reduction, or stopping.

This costs **40 actual training child calls, 40 producer actions, 16 reduction actions and 16 terminals: 72 authored root turns**. The corresponding prior 16-state capture gross time was about 281 seconds, a planning reference, not a runtime guarantee. Authored actions are supervised demonstrations, not paid sampled-policy successes.

## Learning comparison and initial checks

Two arms start independently from the same low66c adapter, pinned Qwen3-4B base and qualified rank-8 FP32-LoRA/BF16-base machinery; child c32 is frozen. Reuse native prefix/mask validation and Adam/checkpoint helpers through a small new local owner, not edits to the old sidecar.

- **Joint:** per-trajectory loss = 0.45 × mean producer-turn CE + 0.50 × reduction CE + 0.05 × terminal CE.
- **Reduction/stop control:** 0.95 × reduction CE + 0.05 × terminal CE on exactly the same genuine trajectories and histories.

Each CE is a current-turn token mean; average trajectories equally. All preceding user/tool/assistant history is masked. Four complete 16-trajectory updates, fresh AdamW, learning rate 1e-4, zero decay, original clipping/settings; save adapter, optimizer and exact exposure/order checkpoint after every update. Select fixed update 4, never the best readout. Joint exposes 72 target turns/pass; control 32. The small terminal weight is a boundary anchor, **not** a claim of useful scalar-copying headroom.

Before any gradient, use the fixed first four balanced capture members for forward-only role and code-span NLL/cost checks. Separately report mechanism code, Python string/query literals, wrappers and terminal tokens; no copied map payload should exist. Require valid native target masks and non-saturated reduction mechanism on at least three of four (mean code-span NLL >0.1); if not, retain a scientific gate stop. Project both four-update jobs from measured per-role forward time × exposure count ×3, with separately budgeted load/checkpoint overhead; reject a projection exceeding 1,200 seconds total training. These are spending gates, not proof of autoregressive skill. Do not enlarge training because CE decreases.

Nominal trajectory count, update count, starting weights and total objective mass are matched; selected tokens, loss allocation and FLOPs are **not**. Joint reduces the control's reduction coefficient. Report role-wise exposures, actual forward tokens and GPU time; any difference is a curriculum-allocation result, not a clean compute-matched benefit of acquisition supervision.

## Paired readout: reachability first, conditional skill second

Evaluate unchanged, joint-4 and reduction/stop-4 with the same accurate prompt, child, caps and paired fresh seeds:

- **Free:** 16 endpoints/policy = four data-heldout contexts × two new user compositions (`u03`; `u01` or `u03`) × two seeds. These are unseen user-set compositions of familiar single/union operators, not novel-operator generalization.
- **Controlled:** eight endpoints/policy = those four contexts × two compositions, one balanced width per coordinate. Make eight new genuine live-accumulator source states (four of each width; **20 actual shared child calls**), then continue at the pre-reduction cut with two accumulator aliases absent from training. Replay only exact qualified source requests/observations, never substitute historical tokens or expose teacher correction/final.
- **Training-state diagnostic:** four fixed training-state continuations/policy, disjoint from heldout reporting, quantify narrow memorization versus transfer. Never train on these sampled continuations or choose a checkpoint from them.

Total: **72 heldout endpoints +12 explicitly in-training-state diagnostics =84 sampled endpoints**, 60 physical child acquisitions for the authored training/controlled sources. Controlled-source costs are shared physically but charged in full per hypothetical standalone endpoint (60 hypothetical acquisition calls across 24 controlled endpoints); free reacquisitions are additional actual costs. Charge capture/reconstruction and all failed work. Training excludes all 64 existing heldout record groups. Those heldout contexts have prior research exposure, so only the new compositions/seeds are fresh; freeze choices before new outcomes and do not call this a pristine confirmatory split. This is four-context exploratory evidence.

Measure authenticated strict final availability, dataset and actual-map correctness separately; actual accumulator creation/update, user-scoped reduction, producer repetition after complete coverage, and final stopping require executed observation-linked data flow, not prompt/AST presence. Keep infrastructure NULL distinct from observed invalid answers, distinguish loops/context failures from execution stalls, and show operational-failure sensitivity alongside available-case bounds. The main useful signal is improved **free faithful scoped reduction plus finishing**, beyond both controls, without replacing errors by loops/NULLs. Training-state success alone is memorization; controlled-only success does not establish reachability.

## Feasibility, cap, and alternative

Preparation can reuse the qualified local source-map, native capture/replay, masking, optimizer/checkpoint and an27 lifecycle assets; changes are the accumulator protocol, multi-role loss and small plans. No model download, RL framework or historical-graph import. Proposed inclusive outer cap **5,400 seconds (90 minutes)** on one A100, with a single shared work clock, per-call/per-episode artifacts, planned NULLs, and owned teardown reserved inside it. Initial envelope: 900s capture/setup, 1,200s gate/training, 2,700s all readout/service transitions, 600s release/slack; measure and freeze exact nested caps before READY. The 20–30 minute target is CPU preparation to an accepted runnable job, not a promised full experimental completion time.

If restart48 shows the unchanged root already reaches/reduces reliably with explicit state packaging, prioritize that interface mechanism and defer SFT; the training bottleneck may largely disappear under the corrected state contract. If the new teacher NLL/cost gate fails, retain the failure and use a small unchanged-root complete-accumulator continuation check, not blind extra epochs. A cheaper old-corpus all-turn mixture remains a second-choice coverage-only ablation, explicitly unable to test faithful live accumulation.

Evidence: original corrective audit `analyses/root-corrective-reduction-sft-live-2026-09-09/REPORT.md` SHA256 `afcff4d61c6398c3b0f3354754a53b2127f537676aa1a0199f15c5b7a4fd279f`; independent completion `completion/REPORT.md` SHA256 `2d73a7ee857dfe27a019b30e9e7cde0e724b6dd51ccf5472d050b05f34ce561d`; original corpus `sidecars/root-corrective-reduction-sft-v1/outputs/attempt-001/capture/CORPUS_READY.json` SHA256 `986e98a07b60c91981ffb0b929cb67ef6f4b7188db46fb8bdbb8e11d0177f15a`. Complete-demo audit and the existing `protocol.py`, `collect.py`, `learning.py`, `train.py`, train/readout plans and live ready-queue assets were read. No external paper is used as evidence that our mechanism is established.
