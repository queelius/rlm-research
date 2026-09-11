# Resume on the newly approved 48-hour A100 allocation

Prepared September 9, 2026, at 17:50 UTC. Read HANDOFF.json for the final handoff state and exact
artifact hashes. The user requested a convenient stop here because another
48-hour A100 allocation is already available in a separate session. The old
instruction to continue until19:07:17 is superseded by this requested transfer.
Do not restart work on the old allocation merely to fill its remaining lease.

## Immediate next action

Inspect the actual new GPU/node/CPU affinity and live research queue, then launch
the prepared **matched complete-demonstration SFT** after the narrow new-node
runtime checks below. CPU analysis should run alongside it. Do not repeat days of
literature review, broad tests or dataset preparation before useful GPU work.

Repository: `/project/alex_phd/repos/rlm`.
Research store: `/project/alex_phd/runs/rlm-research-r4` (R below).
The store and models are outside Git; a Git push does not transfer raw research.
Check that this shared project filesystem is actually visible from the new node.

Next study: `R/sidecars/root-complete-demonstration-sft-v1`.
READY SHA `c9fc31943e81f8b3597e134a5e26b6d9c162e868356d20a37765081fca4b5b23`.
Identity `974c38ad8d0fdbb59f734f7fc2fb8b07e8bb1ac825a868e645ff508ff14a9604`.
RECIPE SHA `50015b9dba692168e2b70dbd10c5c7fc903782212847cca11c872220d1066e90`.
DATA_READY SHA `6590fbaccf1bc7ebd21eb7b1dda77ef178ce7379380d13214dcc757a21c171f4`.

**It has never launched.** There is no training to resume or old optimizer to
recover for this study, and no MAIN launch acceptance/actual waiter was created.
The contemplated operation name `2026-09-09-after-highlr-bridge-complete-sft`
was only a transient planning variable, not a running parent. Use a new operation
with the new allocation's ownership and deadline; never rerun old parent commands.

### What the study tests

Does adding an authentic final-answer demonstration improve the same first-action
training recipe? Capture16 canonical operator-authored programs through the owned
Python environment and **actual c32 child**. Only if all16 produce authentic
scalars, freeze CORPUS_READY and train two fresh-Adam four-update arms from low66c:
same per-example action loss versus that loss plus0.1 terminal loss. Terminal
targets use the actually computed scalar, even when it disagrees with dataset
labels. Observations, previous actions and child tokens are masked. Authored-root
transport placeholders are explicitly synthetic; these traces are NOT RL data.

All three roots (unchanged/action-only/action-plus-terminal) receive the same16
readout coordinates: four16-record contexts, single-user/union questions and two
seeds.64 source groups were selected without labels, outside nine named root
catalogs;32 are helper-training exposed and32 helper-validation exposed. No
global or pretraining freshness claim. No relabeling or nonzero-answer selection.

Outer3600s, work3450s, owned3570s including120cleanup. Capture1080s,
training480s/arm, readout420s/arm and service readiness180s, clipped to shared work.
Every complete update saves adapter/config/Adam/RNG/cursor/corpus/ancestry. The
fresh-only CLI is **not a general resume implementation**. If a future interruption
occurs, use a separately recorded continuation from the last complete checkpoint;
do not restart fresh Adam and call it resume. Preserve partial corpus/readouts and
all failures. The new readout fixes error-produced empty answers to NULL, not0.

MAIN read the new scientific source, preparation, tests and documents; freshly
verified all2533 unique source/input hashes (all under `/project`), and ran the
actual launch.py verify successfully. Six focused tests and four CLI checks
passed in preparation. New code includes13Python files; original native runtime,
serialization, child constraints and checkpoint helpers are pinned and reused.
No fresh full-runtime model qualification is claimed.

Read DESIGN.md, RUNBOOK.md and RESUME.md before launch. One documentation caveat:
DATA_APPROVAL_PIN_AMENDMENT is a JSON file, not Markdown; both its original and
current approval hashes equal d197eb9a…. The approval clarification was already
included when DATA_READY froze. Wording saying it occurred after panel freeze is
inaccurate but does not change any data, target, coefficient or source identity.
Preserve original documents; no re-preparation is needed for that narrative error.

## New-allocation checks that actually matter

- Discover actual hostname, user/UID, `nvidia-smi -L`, GPU processes, assigned
  CUDA_VISIBLE_DEVICES, `os.sched_getaffinity(0)` and allocation end. Do not dump
  the full environment or credentials. Old node was an21, Slurm5771; its MIG
  UUID and process IDs are historical and must not be reused as new authority.
- Confirm source/model/environment paths still exist. CPU Python is
  `/project/alex_phd/envs/rlm/bin/python`; native inference Python is
  `/project/alex_phd/envs/prime-rl-5990b1b/bin/python`; training Python is
  `/project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python`.
  Do not mutate these shared environments. Record the actual driver/CUDA versions.
- Important portability issue: the qualified rootless cache uses node-local
  `/tmp/rlmc.0m4242` and CPUs34,35. The source-only verify can pass while that
  temporary store is absent or those CPUs are unavailable. Read
  `sidecars/runtime-local-cache-v1/RUNBOOK.md`, isolation_short.py and COPY_PLAN.
  Reuse only after ownership/image/allowed-CPU checks. Otherwise make an additive,
  bounded lifecycle-only adaptation with a new mktemp-owned store and allowed
  CPUs; preserve all scientific prompts/data/weights/targets and qualify the
  small native root-child-root seam. Do not rebuild research from scratch.
- Durable image source is
  `/project/alex_phd/research-cache/runtime-images/rpi-v2.kCaOH4/root`.
  Image8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c;
  immutable layer identity/copy map live in the runtime sidecars. Never copy a
  live Podman database or delete another session's ignored environment/cache.
  Existing copy scripts are fresh-only and hard-code old paths/affinity; inspect
  and adapt additively rather than blindly execute them on another node.
- The prior driver library path used580.126.09. Validate the new node, do not
  blindly impose it. Access local provider credentials privately through the
  existing approved configuration; never print/commit them.
- MAIN-only parent coordinator source is
  `operations/2026-09-09-queued-successors/coordinator.py`, SHA
  `7d3294241939297741f26ca657782f757e43b520a717a17a6edac378f32873c1`.
  Existing global COORDINATOR.lock serializes one GPU. Two GPUs would require
  explicitly separate device/port/runtime ownership, not two blind launches.
  New operation must bind READY, exact command, cap, new device/deadline, source
  hashes and predecessor evidence where applicable. Parent verify alone checks
  readability, not all required fields; use a focused authority test.

After these checks, READY's exact argv is the native Python plus
`launch.py run --output <sidecar>/outputs/attempt-001`, under a newly accepted
parent3600s envelope. A lifecycle adaptation must have its own pinned wrapper and
acceptance; do not edit original READY or secretly bypass runtime guards.

## What just finished

- Original child-representation bridge32: low66c+c32; count1/8both, checksum0/8both.
  All32 actual finals available. Matched count label agreement567→593/628 improves,
  but final accuracy does not. Checksum only3/8paired child uptake; no wide64
  batches. Selected code counts final-batch `labels` instead of `all_labels` and
  faithfully reports the wrong scalar. REPORTb0758413…/FINALada5f372… in
  `analyses/root-child-representation-bridge-live-2026-09-09`.
- Same32-coordinate fixed-RL4 bridge: completed536.035s,exit0, GPUempty;
  TERMINAL51d4f894…/STATUSfaedaf5f…. Its outcomes still need an independent audit.
- Same32-coordinate fixed higher-rate-SFT8 bridge: completed506.365s,exit0,
  GPUempty at17:37:29.4825904UTC; TERMINAL644533b3…/STATUS80dbd379….
  Its outcomes still need an independent audit. It has a separately pinned
  descriptive READY correction; executable binding is correct0ba42364.
- Local current-cue replay: all32units/288candidate forwards complete,101.745s.
  Independent audit is sealed: REPORT6db99a0a…/FINALa9ae9fa1… in
  `analyses/leaf-local-cue-replay-live-2026-09-09`. Matching rather than constant
  cues raises mean conditional correct-label probability by0.497 on AG and0.277
  on SST. MAIN read the complete report. These are finite-candidate probabilities
  with a fixed supplied history, not sampled accuracy or internal attention.

The source-only three-policy bridge method is frozen in
`analyses/root-child-representation-bridge-panel-live-2026-09-09`. Its
RESUME_CHECKPOINT.md (SHA bd2a1f4295457c9e4508b5b877f4b26282752e43a0ff50eb7c27c22604bc3eb8)
gives the exact next CPU audit step; do not rerun completed GPU evaluations.

The prior avoidable scheduling gap after replay was899.373711s (14m59.374).
Do not hide it as training or useful inference. The stop after17:37:29 is instead
the user's requested transfer to an already available48-hour allocation.

## Research priorities and reading route

Read analyses/CURRENT_SUMMARY.md, PROMISING_RESULTS.md and analyses/README.md.
The new linked catalog is `analyses/research-factory-2026-09-09`. Its first bounded
slice is complete: nine sealed reports, eight questions, thirteen claims, six
decisions and three publication candidates, with evidence cutoff17:32:51UTC.
MAIN read its readable summaries and claim statements, checked its five content
hashes and58 unique IDs, and freshly verified all fifteen local source hashes.
This is linked curation, not another raw audit or complete historical coverage.
The new replay result and two pending bridge audits await an additive catalog
version. Consult coverage/cutoff and HANDOFF.json. Older
cross-experiment-synthesis covers only01:35UTC and stays immutable.

Strongest current component evidence: matching source IDs improve batched labels
across data/models; reminder timing and contradictory IDs locate a behavioral
correspondence effect. It is not attention proof, guaranteed whole-input accuracy
or an established whole-RLM gain. Controller SFT/RL gains are real but limited and
uneven; initial-action-only training failed to teach filtering. Preserve negative
and NULL evidence alongside the promising results.

The user's new `new-ideas/ideas.md` was read completely and must remain unmodified.
Top broader direction: ideas1+5, supported by3—learn what information must cross
a recursive boundary, then test valid partition changes and unfamiliar operation
combinations. A hand-constructed lossy summary versus full incidence is only a
diagnostic, not learned composition or novelty. Include ordinary child reports,
exact-program and nonrecursive baselines; keep correctness separate from agreement,
and input length separate from recursion depth/compute. Idea6 (sufficient compact
continuation state) is a separate promising line;2/4/7 are later priorities.
The specific OpenReview counterfactual citation was not verified; do not assert it.

After launching the prepared SFT, prepare two useful successors on CPUs: the
approved supplied-map/reducer diagnostic on the same new panel, and a small
cross-partition task-family pilot informed by the new ideas and neighboring
structured-decomposition-benchmark. Neither is implemented/READY yet. Preserve
the distinction between executable plans, approved designs and hypotheses.

Continue the user's research factory: source-linked questions→experiments→claims
→decisions→follow-ups; contrary evidence, claim limits, primary literature, reusable
figures and publication gaps. Generate new questions from results and retire weak
recipes. CPU organization must overlap GPU work. No blocking design questions;
user delegates principled research decisions, downloads and isolated environments.

## Repository state

Main HEAD `5a7ea61d1e3b84d561217a1fe363de623263b467`, ahead origin/main7.
User-owned untracked `new-ideas/`; MAIN updated docs/RESEARCH_OPERATIONS.md for the
research-factory priority. Any later navigation edits are listed in HANDOFF.json.
No push, cache deletion, environment mutation or artifact relocation was performed.
Do not mistake these shared-filesystem artifacts for files already on GitHub.
