# September 8 resumption decisions

The allocation has one A100 40 GB, not two. Preserve inherited CUDA visibility. Parallelize
CPU preparation and analysis, then alternate GPU rollout and optimization phases. The user is
away and explicitly asks for uninterrupted autonomous progress; record unresolved preferences
here rather than asking blocking questions.

## Decisions taken

- Defer home-cache migration, as requested after checking the increased 1 TiB quota. No home
  files have been moved or removed. HF model weights account for most cache usage; inventory is
  in the neighboring home-audit directory.
- Reassess actual artifacts instead of trusting the stale live queue. Distinguish completed
  evaluations, admitted update batches, real optimizer steps, and heldout improvements.
- Start the smallest balanced client-path comparison on the frozen 4B model. This should tell
  us whether the training interface disrupts Python calls before interpreting failure as an
  inability to plan or a need for different rewards. It is an exploratory systems/behavior
  comparison, not evidence of model learning.
- Prepare a sequential one-GPU 8B RLVR run in parallel. Remove the arbitrary exactly-two-turn,
  exactly-one-leaf-call admission rule. Keep strict task correctness and causal training-token
  alignment; these measure different things.
- Prioritize plan discovery/transfer and a concrete harness intervention after the interface
  question. Longer contexts alone are not a sufficient demonstration of compositional
  generalization. Include supplied-plan and free-choice controls with equal tool/budget access.

## Allocation restoration

The initial server config passed the API key as a string, but installed vLLM 0.28 iterates a
list of keys. It therefore rejected the intended complete key. Stopped only the owned process
group and created a new launch configuration with the key as a one-element list. Attempt 001
and attempt 002 have separate service records and logs; no scientific episodes ran in the
first attempt.

The old rootless container image was stored in node-local `/tmp` and did not survive the
allocation. Rebuilt it from the same pinned Python base using the inspected existing build
script. The derived image has a new ID because apt dependencies/build timestamps differ.
All conditions in the new paired experiment use this same rebuilt image. Record its identity
and do not claim exact image equivalence to September 2.

## Questions saved for the user (nonblocking)

- After the exploratory comparisons, which application most interests the advisors: document
  aggregation, structured compositional reasoning, or temporal/streaming inputs? Default now:
  retain document aggregation as the working testbed and add unseen layout/composition controls.
- Is a later two-A100 allocation likely to be 40 GB or 80 GB per GPU? Default now: design every
  current job for one 40 GB device; additional GPUs will improve throughput, not be required.

## Adaptation after the client experiment

Both48-episode qualification runs completed. The unchanged nonthinking4B model used Python
on0/24 old training-client episodes versus16/24 after removing a non-native empty thinking
prefill. Strict correctness changed0/24 to3/24. Repeated Eval control totals stayed18/24 Python
use and2/24 correctness, though individual generations can vary with serving state. This is
an interface repair with no optimizer update, not a learning claim.

The corrected path yielded mixed rewards, so the next learning attempt uses the already-loaded
4B model. Fresh training40 and heldout-before16 run alongside a56-episode procedural-hint
comparison. Preserve all captured actions and observable policy errors. The prepared8B workflow
remains next in the queue; it need not displace an operational4B learning opportunity.

Before heldout-before collection, declare the primary endpoint on the7 non-answer-revealing
source-heldout tasks (14 episodes). Known source ID12000052 exposes its answer via a single
allowed label, so it is excluded from the primary endpoint. Preserve the original frozen8-task/
16-episode collection for historical comparability and report it separately. This exclusion is
based on prompt inspection, not outcomes. The context group has been evaluated in earlier
experiments, so later results are exploratory, not fresh confirmation.

Prepare self-SFT from the same40 fresh trajectories as an independent control, starting from
the identical step0 adapter. Use successful model actions only. The first SFT and RLVR spikes
are not compute-matched; their actual optimizer steps/action tokens must be reported. Any
promising difference needs a matched followup and new context groups.

## First updates and the next mechanism test

Self-SFT completed six real optimizer steps on all six verified positive episodes (2863 action
tokens, one epoch). Every checkpoint includes adapter/optimizer/RNG/cursor state. Primary
heldout stayed2/14, with all14 paired outcomes unchanged. The only secondary gain was the
previously identified answer-revealing task. Do not use it as evidence of semantic improvement.

The first RLVR attempt failed before optimizer.step. Two concrete input defects were identified:
Prime's adapter key names did not match PEFT, and the FP32 source LoRA tensors were being loaded
into BF16 adapter parameters. An additive key conversion and FP32 adapter loading preserve all
504 original tensors exactly. No source weights were edited. The base model remains BF16.

The separate serving/training probability discrepancy is sparse: mean absolute log difference
0.00747, eight of6454 actions above0.5, ratio range0.3641 to1.8591. A real GPU comparison showed
that changing the output projection precision did not remove it. The subsequent RLVR attempt
therefore uses a separately declared one-step token importance correction, not an undocumented
relaxation of the failed maximum-only gate. Cap weights at2, preserve all raw probabilities,
and report distribution/gradient/weight-change diagnostics. This is approximate conditional
correction, not exact trajectory importance sampling or a guarantee of policy improvement.

An executable recursive-call example has produced genuine child calls and error-responsive
batch sizing in the development probe. This gives a concrete action-headroom question to
follow up on the original weights and eventually new documents. It does not establish learned
planning: the example supplies parsing/API structure, and some child classifications remain
wrong despite correct aggregate answers. Investigate train-only source labels and counterfactual
documents before deciding whether outcome rewards alone are adequate.

The eight-billion-parameter followon is being amended before launch for the same FP32 adapter
identity issue and its separate raw-versus-temperature-processed logprob contract. Preserve
the original unused spec. These are demonstrated compatibility fixes, not broad hardening.

## Research operations

Allocation inspected around 19:15 UTC; first inference process launched at 19:21 UTC. The
initial idle interval covered stale-run inspection and adapting an unexecuted two-GPU runner.
The avoidable part is recorded: no single-GPU ready run existed despite one-GPU resources.
Follow-on preparation now overlaps model service startup and execution. Do not use full
repository tests or comprehensive source-tree seals to delay independent exploratory runs.

An avoidable successor-launch delay occurred after the RLVR service became ready at20:28:02;
its first evaluation launcher started around20:29:40 while the controller was analyzing future
directions. Record this roughly98-second idle interval rather than describing loaded GPU memory
as utilization. Future service starts should chain a ready evaluator to readiness automatically;
the prepared8B coordinator already owns its complete sequential phases.

## 21:46 UTC: move from saturated root policy to supervised child competence

The8B pipeline completed calibration12 and training24 without a usable mixed-reward
group. No optimizer ran; the measured root programs were identical across36 episodes.
Do not keep sampling nearly deterministic root actions merely to occupy the GPU.
An audited recurring worker classification error, together with weak4B record-level
labels, makes child competence a better immediate training target.

Definitions/schema comparisons finished72 development calls and720 validation calls.
Canonical correctness increased substantially but absolute performance remains limited
outside the OOLONG validated pool. TREC subtype composition differs; retain classwise
and source-provenance interpretation, not a generic reasoning claim. Freeze today's
definitions; do not adapt them to the just-inspected validation mistakes mid-comparison.

Launch full leaf SFT on5065 training groups, two epochs,128 steps, exact original LoRA.
Selection uses300 validation groups only, then489 test groups. Teacher source labels
are explicit supervised targets, not fabricated policy trajectories/logprobs. Main
purpose is to test whether fixing a local semantic bottleneck improves a composed RLM.
Next role-routing comparison must keep root weights fixed and verify actual child alias.

GPU operation: rootless MRCR12, directMRCR6, validation720 and definitions12 all
completed while CPU SFT preparation proceeded. There were avoidable short gaps between
successor launches; loaded inference memory was not useful compute during those gaps.
Definitions12 was observed complete at21:43:49; the owned inference group was stopped
and SFT launched21:45:19. This90-second observed transition includes source/ownership
checks and service release. Earlier exact completion/launch times remain in individual
attempt artifacts; do not invent an exact total idle duration. Keep two CPU follow-ons
prepared during this longer training job, and use actual model/step events as evidence
of work rather than MIG memory occupancy.

## 22:10 UTC: completed leaf training and composed followups

Two-epoch SFT completed128 real updates in705.625seconds of accumulated training.
Frozen validation rule selectedepoch2 (250/300 versus245/300). Matched greedy HF
test improves355/489 to473/489; baseline7 invalid five-item arrays become0. This
strict metric includes whole-array validity, so a separate itemwise/alias analysis
must distinguish formatting from semantic gains. One trainingseed and a familiar
public taxonomy do not establish novel classification or general reasoning.

The definitions-only full-RLM comparison stayed2/6 vs2/6 with sixpairedties despite
substantial child improvements. Every definitions child received the definition;
root code still mishandled JSON strings, category minima and final arithmetic.
One root used one-record calls and hit nano's internal64-subcall cap: no outer
censoring, but an actual internal budget effect. Earlier wording 'all recorded'
must not be interpreted as no budget effect.

Dual-adapter inference now tests fixed original root with original versus selected
trained children. First12 reuseddev cases plus48 newly composed heldout-source cases
run concurrently. A fixed Python batching/aggregation control is queued to determine
whether root handling hides an otherwise useful child improvement. These experiments
are not parameter-count or total-inference-budget-matched direct comparisons.

Next learning candidate: root-only RLVR while keeping the now-stronger child fixed.
Terminal labels alone previously credited unreliable child/aggregation programs.
Do not silently relabel past rewards. Instead collect fresh root actions on new
training contexts with role identity and exact native probabilities, treat child
answers as fixed-policy environment observations, and train root parameters only.
Require observed mixed reward groups; if root probabilities saturate again, pivot
task/prompt support rather than indefinitely resampling an uninformative policy.

## 22:39 UTC: learned child, coordinator bottlenecks and batch-shape transfer

The completed SFT's test gain is not just enum formatting: itemcanonical374/489
becomes473/489. Strict whole-array gating amplifies355/489 to473/489. Selected by
validation only, but all current composition followups reuse this inspected source.
The free RLM remains weak:2/6 unchanged on development and4/24 to6/24 on newly
composed contexts. In contrast, a fixed Python aggregation routine yields1/24 to15/24
with five-question child batches. Some aggregate improvements are contract gating
and count errors can cancel; keep item and aggregate endpoints separate.

An independent audit found first root actions differed before any child despite
identical forwarded first requests/seeds in18/30 pairs. These differences cannot be
caused by the selected child's responses. The observed paired full-RLM differences
are noisy whole-system measurements, not clean evidence that child weights changed
root planning. A future unchanged-weight replay estimates this implementation noise.

Batch16 also reaches15/24 trained strict counts with192 rather than624 calls and
86372 rather than248804 logical input tokens per arm. It loses some record accuracy
and one complete-array contract; do not hide that trade-off. Freeze two endpoint
batch variants (1 and64) before new calls to test a simple harness efficiency knob.
Their1024 output cap differs explicitly from prior256 to allow whole-document arrays.

Launch root-only credit collection now, not after broad review. Its source/routing
qualification is complete, and training recipe is frozen before mixed-group outcomes.
Only the root's own current actions receive gradients; improved child remains fixed.
One first update is an implementation/learning-signal probe, not a claim that one
step is an adequate RL training campaign. Continue with fresh-data rounds or pivot
according to actual reward variation, process traces and heldout behavior.

Operations: nativeMRCR6 ended around22:20; batch16 ran around22:25; successors did
not start immediately after its quick completion. Root40 began22:34 after a
compaction/resumption and Phase1 readiness at22:31:48. These intervals included
avoidable idle reserved GPU time, not utilization merely because weights stayed
loaded. Exact job times remain in ATTEMPT/STATUS files; no invented utilization
percentage. Three independent inference clients now overlap CPU trainer/audit work.

## 23:43 UTC: separate output contracts, semantic correspondence and root learning

Exact-cardinality grammar restores singleton trained strict counts5/24 to16/24
without changing any of1536 first labels. At64 it restores validity but not count
accuracy (0/24 both weights), and trained last-quarter accuracy is81/384 versus
374/384 in the first quarter. All64 inputs are physically present. Original
weights also fail, so this is an inherited/remaining operating-range problem,
not proof that five-item SFT caused it. The7056-request audit is sealed.

Proceed with two full original-initialized leaf SFT curricula: same5065 groups
twice, sizes1/5/16/32 versus1/5/16/64, fixed finalepoch2. This tests repair and
extrapolation, not generic classification novelty. A is running on the GPU;
B has an actual automatic wait-and-launch process (session28844), not just a
written queue. Final64 prompts match the frozen HF probe exactly; semantic
HF/vLLM equivalence did not imply physical token equivalence because tool JSON
key order differs. Retain the distinction instead of rewriting the probe.

The root-only RLVR pilot completed one real AdamW/TIS update:10500 action tokens,
23.866 optimizationseconds, nonzero gradient/update, no child/observation loss.
Initial/unchanged/post validation totals2/8,4/8,2/8 do not support a learning gain.
An independently initialized eight-round campaign is still appropriate: it asks
a longer-training question with fresh groups, fixed child and persistent Adam.
Its source/termination recipe remains separate from the pilot; no reward relabeling.

The sibling adaptive-context design remains conceptual guidance, not a demand
to build its whole artifact platform first. The current evidence distinguishes
worker competence, aggregation reliability and choosing a decomposition. Evolved
integrators suggests bounded inspectable harness candidates and charging all
search costs. It does not justify assuming adaptive batching outperforms the
best fixed batch; that needs a direct cost-and-accuracy comparison on new groups.

Approximately17minutes between post validation completion and resumed launch
were loaded-but-idle GPU time. Record this as opportunity cost. The B waiter
and continuous RL campaign reduce dependence on assistant turn timing; never
substitute loaded memory or artificial filler for decision-relevant GPU work.

## September9 00:18 UTC: no reliable size extrapolation yet; prioritize sustained RL

Mixed-size A completed206 updates and1151.455 optimizationseconds. Fixed5 test
477/489 is high but only four more than the previous473/489: do not turn that
small unreplicated difference into a headline. All six64-item free outputs fail
the exact array contract; five truncate. This does not prove every early label
is wrong, but the trained interface is not reliably usable beyond its32-item
training support. B, which explicitly includes64, automatically started00:01:35.

Next GPU priority is the ready eight-round root-only RLVR campaign V2, not more
CPU polishing. Session39335 now owns its automatic launch after B exits and the
GPU is empty. Its original-root/fixed-old-child inputs are independent of B, so
an unsuccessful B does not block this useful job. Source and live events reside
in operations/2026-09-09-succession. No duplicate manual campaign launch.

Queue small followups after RL: record-index/repeated-question and rotation
controls on the old child; SST-2 transfer on all four weights; and free/schema64
comparison on those weights to distinguish contract failure from correspondence.
The new schema comparison is chosen after seeing A's failure but before B's
outcome; it is exploratory and reuses development groups. No original primary
score is replaced by schema-repaired output. Two warm service stages amortize
model loading. Existing core already supplies FINAL_TEXT; a separate nano-side
shared-prefix direct-commit study measures the cost of the extra generative final
turn, not a claimed novel final API or a change to the root learning campaign.
