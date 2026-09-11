---
status: design_only_not_approved_for_implementation_or_launch
supersedes_assumptions_not_files: 2026-09-09-qsr-sparse-reward-response.md
original_note_sha256: 4de8039723b9519bc427d65934422febd91d76ac566c1c3b845ebeea659eae9e
read_depth:
  original_proposal: complete
  qsr: "Complete owner.py, qsr_train.py, qsr_common.py; targeted qsr_native prompt and qsr_data operator/split construction; all12 window timing/cursor receipts, not final efficacy traces"
  joint_sft: "Complete train.py, joint_learning.py, joint_protocol.py and capture/readout collect.py; capture/gate/train/phase timing receipts, not a new outcome audit"
  literature: "No new paper search/read; original note's literature scope remains unchanged"
evidence_boundary:
  qsr_windows: 12
  qsr_adam: 10
  qsr_trained_final: pending_at_design
  qsr_unchanged_final: "MAIN relayed2/48 planned,46available,supported0/12,zero child tokens; not independently rescored here"
  ce_transfer_outcomes: "Not read; separate prospective audit methods already sealed"
  starting_policy: "low66c is prior success-trajectory SFT step8, NOT released4B; no silent start switch"
timing_manifest:
  files: 72
  canonical_path_to_sha256_digest: 1014cb72631246e55e2f5a6e9359acaff592a74f3669e72703fdae73e0f7dd4f
  construction: "QSR OWNER_RUN/SELECTION, all12 WINDOW_RESULT, present TRAIN_COMMAND/TRAIN_EXIT and collect-*-COMMAND/EXIT; joint two training RESULT,gate RESULT,joint checkpoint0004 state,two teacher capture COMMAND/EXIT,and three free COMMAND/EXIT; absolute-path keys sorted,compact canonical JSON"
options:
  reachability_screen: {trajectories: 36, sft_updates: 12, policies: 2, final_calls: 48, work: 5700, owned: 5880, outer: 6000}
  matched_warmstart_rl: {trajectories: 36, sft_updates: 8, scheduled_windows_per_branch: 4, train_calls_per_branch: 96, maximum_adam_per_branch: 4, final_policies: 3, final_calls: 72, work: 10500, owned: 10680, outer: 10800}
---

# Operator warm-start: first establish the right start and a reachable transition

Do not launch rank2 on the original “inaccessible reward” premise. QSR completed12 scheduled windows and10 actual Adam updates in4155s: reward is demonstrably reachable, though held-out efficacy is still unresolved. MAIN's low66c baseline result is poor, but it is a **narrow success-SFT8 policy**, not a released-model baseline. The separate root-lineage/released4B calibration should determine whether that common starting policy is an avoidable handicap. This note neither selects a replacement checkpoint nor duplicates that calibration.

If compact-role/raw CE fixes the task, prioritize a fresh matched harness readout, not warm-start training. If released4B calibration exposes a low66c regression, require a separately approved common starting binding and repeat the design with that same start in every relevant arm. Do not relabel “unchanged” as “released,” mix starting weights between branches, or select a current QSR/joint checkpoint using test performance. A strong QSR trained final would make warm-start an efficiency/increment question, not an emergency reward rescue.

## Measured feasibility, not additive wishful caps

| Actual job | Measured elapsed |
|---|---:|
| QSR24-root collection,12 windows |175–324s; median194s |
| Complete QSR window including service/export/train |276–485s; median336s |
| QSR actual training process,10 updates |44–149s; median60s; total685s |
| QSR last four complete windows |1452s |
| Joint16 full trajectories /40 child calls /72 authored root actions |290s capture |
| Joint SFT4,16 trajectories/pass |183s core;198s including load/checkpoints |
| Reduction/stop SFT4 |94s core;111s total |
| Joint free16 unchanged/joint/reduction |170/378/281s, excluding service startup |

The original720s/RL branch is less than half the observed last-four-window duration. Its several180s service allowances were not meaningfully contained in5400s. Training-only token CE is cheap relative to native rollout/service cycles; spending the whole budget on more epochs would not test free continuation.

Thirty-six balanced width4/16 trajectories on16-record contexts require90 actual child acquisitions and162 authored root actions:90 producers,36 reductions,36 stops. The old72-action corpus had5016 target tokens and113096 full forward tokens/pass. Linear same-length proxies are11286 target tokens/pass; SFT8 ≈90k target/2.04m full-forward-token exposures and822s core; SFT12 ≈135k/3.05m and1232s; SFT16 ≈181k/4.07m and1643s. These are NOT measured new costs: q+hex IDs, weights, new code and longer genuine observations increase prefix/attention cost. Capture36's linear proxy is653s plus startup/release, not600s safely inclusive.

## Common corpus and controls

Use the first six existing QSR training contexts,18 supported operator/scope queries ×two layouts =36 fixed complete trajectories. These96 source groups are exposed QSR training data and child-training-exposed, not new data. Keep all16 actual records per acquisition trajectory; query-sensitive scope/operator application is taught at reduction, not an invented claim of learned selective acquisition. Count/distinct-user/visible-weight sum are genuine different operators, unlike retired BROAD16 whole-context/category substitutions. Balance variable names independently of operator, scope and width.

Authored actions execute in the actual same native REPL: import/load real records, acquire through unchanged optional typed c32 transport, strict-decode real child responses into a live accumulator, apply requested user scope and operator to those variables, print the actual scalar, then return the observed scalar with native Answer syntax. Never embed copied maps, host labels or gold answers in root targets. Keep semantically wrong child labels and their consequent scalars. Structural capture failures stop corpus admission; preserve all36 slots/raw attempts, no replacement, repair, success-only subset or acquisition resampling. No old evaluation trace enters training.

Use one explicit role and unambiguous scope wording COMMON to capture, both RL branches and all final policies. Which role/start is chosen requires MAIN review after CE/lineage evidence, before freezing; it is not a hidden per-arm intervention. Preserve teacher native prefix IDs, current-action-only suffix loss and all child/observation/history masks. Keep the qualified joint masses .45 producers/.50 reduction/.05 stop (equal producer share per trajectory), rather than silently adopting the original note's new .40/.55 recipe. Report both nonliteral acquisition/accumulation/reduction NLL and copied-literal/control/terminal NLL. Nominal loss mass is not gradient share. Native stop targets are retained but near-zero scalar-copy CE cannot qualify mechanism headroom.

A fixed six-trajectory forward-only gate spans all three operators and both layouts/scopes, not selected by correctness. It validates executable state, nonliteral target spans, remaining nonterminal CE and measured full-corpus time projection before gradients. Freeze the update count before launch; a failed cost/headroom gate is not permission to pick an easier corpus or silently shorten the recipe. Preserve all completed checkpoints if later capped; incomplete updates do not commit.

## Two options, conditionally ranked

**A — prefer a free-reachability screen if transition learning remains unproven.** Fixed12 complete36-trajectory updates versus the same unchanged start, no RL.48 fresh free endpoints: four predeclared QSR readout contexts00,01,08,09 (two16-record/two32-record), the three held-out cells count-union/distinct-all/weight-single, two fresh paired seeds, both policies. These groups are disjoint from training but research-exposed; no whole-system novelty claim. Teacher states are not readout starts. This directly asks whether diverse full transitions change free acquisition→operator→stop behavior across source/size/composition changes. Twelve passes remain432 repeated trajectory exposures, not general adaptive competence.

6000s outer =5700 work +180 owned cleanup +120 outer margin. Within work reserve capture900, forward gate/SFT2700, mandatory finals1800 (900/policy, including startup/release), finalization300. No optimization may consume the final reserve. If the six-example cost gate projects beyond the SFT allocation, stop and preserve the corpus; do not perform blind partial extra epochs. A capped trained arm is explicitly last-complete, not falsely “SFT12.”

**B — only when evidence warrants the RL increment question.** Fixed SFT8 from the common approved start; then RL-only and SFT8→RL each receive four fixed new-window identities on QSR training contexts06–09,24 free samples/window (3×8), paired inputs/seeds and unchanged numerical objective, terminal reward and strict training admission. SFT groups and RL groups are disjoint; final groups above exclude both. No zero-variance refill, forced recursion, shaping, copied teacher replay or optimizer update from partial windows. Three final policies are RL-only last-committed, fixed SFT8-only, SFT8→RL last-committed,24 fresh paired free endpoints each. This identifies an RL increment over SFT and warm-start benefit over matched RL, but not equal total data/tokens/FLOPs: the warm branch has extra SFT data/compute.

10800 outer =10500 work +180 cleanup +120 margin. Work reservations: capture900; gate/SFT1400; RL2600/branch; mandatory finals2700 (900/policy); finalization300. These sum exactly10500. Retain the existing1440s minimum remaining-time guard before starting a native RL window;2600 supports all four under measured late-window timings, but slow loops can leave planned slots unattempted. Four scheduled windows are NOT guaranteed four Adam updates. The block caps intersect unchanged per-operation caps and can stop learning; finals retain their allocation regardless of signal. Fixed service-phase order remains a time-order limitation. SFT16 is not a free upgrade within B: it roughly doubles SFT8 cost and threatens the readout reserve; study16 separately, not by test-selected checkpoint extension.

## Exact reuse and decision boundaries

Reuse joint `collect.py:episode` actual capture/provider seam, `joint_protocol.py:producer/visible_maps/target_spans`, `joint_learning.py:losses/update`, and `train.py:load_model` plus authenticated checkpoint writer. They are **not drop-in36/8–12 entrypoints**: current code hardcodes16/four, count-only correction and four-example gate. A new isolated small parameterized wrapper must change corpus cardinality, operator action construction, fixed update count and group-aware binding while preserving numerical masking. No edits to live/sealed files.

For B reuse QSR `qsr_collect.py`, `qsr_export.py:export_attempt/authenticate_export`, `qsr_train.py:authenticate_group` plus its pinned campaign trainer, `qsr_common.py` generation/transition semantics and owner collection/train seams. New namespace/plan/generation binding is required; the existing owner is a hardcoded12-window/low66c campaign and cannot merely be rerun with a different adapter. SFT and RL have separate Adam/RNG state; each RL branch begins fresh RL Adam0 from its authenticated starting adapter. Save every complete SFT update and RL commit with optimizer/RNG/native-source ancestry; save every consumed no-op window. Resume, if separately authorized, begins after the last consumed window/complete update, never replays a committed group; unfinished captures/rollouts remain immutable failures, not automatic retries.

Choose A only if CE/lineage support a teachable nonterminal gap that is not explained by the role alone, and QSR/transfer outcomes leave free transition generalization unresolved. Choose B if that transition is sufficiently credible and the open question is whether it improves matched RL learning/held-out execution. If maps are primarily semantically wrong, investigate child evidence quality instead; preserve those errors rather than teaching gold-corrected demonstrations. If QSR improves robustly, or a common role/start repair suffices, defer both. These are conditional research proposals, not training authorization to occupy a GPU.

### Source identity anchors

QSR owner `bcb3fdc0fa73321cb8268736cae1790268afe9b79d8c83fa04207f2fa74f3c8b`; qsr_train `a5064c270f80e157945775accde4e57cd9c5f9e82d1bb17862a118786cb13878`; qsr_common `4f6a3cd85b95dfb6b005eb47f173b1bda2e84ba2f14e0f4010e327c055fe552d`; QSR SELECTION `d9ca1faf43c280f4b882bd3b27ca0deaad7a40b3ca4d1ce570453d6e42b1a87c`.

Joint train `6491520cf407642f9607413621591cb1dd5c6b139f96c90d784880f4f1f6e405`; learning `b5d063afe883d1cbaa49a6b50bfa9d0ca561815fdc2d1617e905724dcb69b4db`; collect `f2e0d2adcfe01ee562488a98e24037781ab81f2f7daab9462eecf7098f4d93ac`; protocol `9cd776cf132784d0c589266d89e2e9613fd83a6f3126ff1a5f95657d6359a8b7`; joint training RESULT `954122d4c2b55ed982ea48d50f5f00a2007703c91e3cea76963c9d0c3a59f921`; gate RESULT `e752505425e34a31475514d375c92dc9b669ca0fd507b60d0a422be137c6da39`; joint checkpoint4 state `df337c996a93a53248008cebb6941afed6722ea851820fa68e10e11f7cfd337a`. Full timing-manifest construction and digest are specified above. No final efficacy scores were inferred from training CE or cursor advancement.

### Post-review fixed-dose clarification

MAIN reviewed the initial memo SHA `14564dff752a2c8ab6c8c0d1dc36e1c66b8352429c1aa8db58687f82660a0819`; implementation remains unapproved. In B, failure to complete authenticated SFT8 makes SFT8-only and SFT8→RL unavailable planned treatments: checkpoint7 must NOT be silently substituted into either. “Last committed” is the declared rule for RL branch updates only. In A, an optionally evaluated capped SFT checkpoint is a separately labeled partial-recipe diagnostic, never the primary fixed12 treatment. Checkpoints remain preserved regardless. The2600s RL allocation plus1440s launch guard supports four windows at observed typical timings; it never guarantees all four will start or produce Adam updates.
