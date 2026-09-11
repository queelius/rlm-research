---
schema: research-feasibility-v1
id: idea:operator-corpus-diversity-decision
as_of_utc: "2026-09-10T00:38:00Z"
status: decision_note_no_implementation_no_download
recommendation: B_72_unique_x_6_passes_after_reference_gate
gpu_authorized: false
---

# Is 36 trajectories × 12 passes enough diversity?

## Decision

Do **not** promote the proposed 36×12 recipe as evidence for broad native competence. If the
fixed24 warm-reference calibration shows a reachable nonzero transition, prefer **B: 72 unique
trajectories × six passes**, with the same 432 trajectory exposures and approximately the same
projected training-token budget. This is the smallest comparison that materially increases
context/template diversity without another model or dataset acquisition. It still teaches one
bounded TREC-derived record program, not a general RLM policy. If calibration shows no authentic
reduction, spend a small reachability/interface/teacher-NLL diagnostic before either SFT option.

Decision-time context from MAIN, not independently rescored here: the completed contract/evidence
panel found compact-role raw 0/6, compact-role supplied-map 2/2 available on only one context,
native raw 1/5, native map 0/3, plus six source-gated NULLs. The sealed two-context transfer found
joint nonzero 4/4 versus unchanged 0/4, but no live-accumulator scalar and many loops. Thus role
wording alone is not a rescue, while full-transition supervision has a narrow positive signal whose
mechanism and breadth remain unresolved.

## Hard inventory

**A — proposed 36×12.** No 36-example native corpus currently exists; the available object is a
[design](2026-09-09-operator-warmstart-measured-feasibility.md) (SHA
`75c08ab6…0ff46b`). Its ingredients are cached: six QSR training contexts, 96 records/groups,
18 operator/scope queries (count, distinct-user, weight; single/union/all), and two acquisition
layouts. All source groups are QSR/research exposed and c32-training exposed. Capture would require
90 real c32 acquisitions and 162 authored root actions. The measured proxy is 653 seconds capture;
12 passes repeat each trajectory 12 times (432 exposures), about 135k supervised target-token and
3.05M full-forward-token exposures, and 1,232 seconds optimizer core. The complete proposed screen
reserves 6,000 seconds on one A100-40GB including two-policy readout. These are estimates, not an
implemented corpus or timing guarantee.

The completed [joint16 corpus](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/root-joint-state-reduction-sft-v1/outputs/attempt-001/capture/CORPUS_READY.json")
(SHA `13b26045…6f0f2`) is narrower: 16 trajectories, eight contexts, one familiar category family,
single/union scopes, 40 child calls, and four passes. Moving to A adds all three operators and more
actions, but its six contexts, one record schema, one question style and heavy replay can still
teach a handcrafted acquire-map-reduce-stop routine.

**B — recommended modest breadth.** Build 72 native trajectories from all 12 already cached QSR
training contexts (192 records/groups): three predeclared operator/scope cells per context × two
layouts. Rotate four semantically equivalent question templates, accumulator names, and batch
widths 4/8/16 independently of operator and answer. Use six passes: 72×6 preserves A's 432 example
exposures; a linear length proxy remains about 135k target and 3.05M full-forward tokens, while
capture doubles to roughly 1,306 seconds (180 child acquisitions, 324 authored root actions).
Reserve about **7,200 seconds outer**: 1,600 capture, 2,700 gate/training, 1,800 mandatory matched
readouts, 900 service lifecycle, 200 finalization. Freeze a fixed checkpoint and stop rather than
shorten after seeing loss. Exact tokenization and a forward-only gate must replace linear estimates.

B's new uncertainty is useful: does diversity, rather than twelvefold replay, improve free
acquisition→accumulation→operator→stop behavior? It does not isolate which diversity dimension
caused a gain, establish cross-domain transfer, or create unseen data. Use one unchanged starting
root and c32 child; preserve every genuine child error and its downstream scalar. Never insert gold
labels, repair a trajectory, reroll failed captures, or select successful teachers. Compare against
the unchanged root on fixed source-disjoint readouts, with nonzero accuracy, availability, and
executed evidence use primary. Retire/deprioritize only this routine if gains are formatting-only,
zero-only, or absent outside its templates.

**C — original-paper assets.** The [RLM paper](https://arxiv.org/abs/2512.24601v3) reports SFT of
Qwen3-8B from 1,000 successful large-teacher root trajectories with an 8B child—far more diversity
than 36 demonstrations. The authors' [official repository](https://github.com/alexzhang13/rlm)
releases inference/training code; the locally cached commit `854e688f…e270` contains no trajectory
or SFT-dataset files. The official Hugging Face organization presently exposes only the OOLONG-Pairs
dataset, not those 1,000 trajectories. It does release the
[paper's 8B checkpoint](https://huggingface.co/mit-oasys/rlm-qwen3-8b-v0.1) (MIT) and a later
[30B-A3B LoRA](https://huggingface.co/mit-oasys/rlm-qwen3-30b-a3b-v0.1) (Apache-2.0; model card says
eight A100s). Neither is weight-compatible with this Qwen3-4B native stack, so metadata-only review
is warranted; do not download them as an SFT shortcut. Recheck the official organization once
before a future corpus freeze.

The dialogue-game [Acquire–Repair–Preserve paper](https://arxiv.org/abs/2608.28458v1) is supporting,
not transferable proof: broad success-only SFT produced most gains, while narrow repair had
within-family and sign-inconsistent effects. Its lesson here is to buy real trajectory diversity
before repeated local repair—not to repair c32 outputs or import game transcripts.
