# Unattended breadth experiments

This is a finite exploratory inference campaign, not new RL/SFT training and
not a run of the unrestricted RLM controller. It compares small fixed harnesses
that isolate information passed through helper calls. No Codex or external
model API is called. It can continue after Codex exits while the GPU allocation
remains alive; it cannot preserve an allocation that the scheduler cancels.

## Scientific questions

Do concise summaries or evidence-preserving helper returns outperform a direct
answer? Does the effect depend on task type and two-way versus four-way division?
Does restricted exact arithmetic help FinQA? Do the patterns occur in both
released4B and8B models? These are different pretrained models, not a controlled
model-size intervention. Neither model uses a research adapter in this campaign.

Data: answerable MuSiQue, FinQA, BoolQ, disjoint AG News count groups, and
LongBench v2. Source records and sampling are frozen in data/cases-v2.jsonl;
licenses, revisions and acquisition hashes are in data/MANIFEST*.json.
The HF split named train for LongBench is its released benchmark, not evidence
that these items are appropriate for model training. No training uses it here.

Methods: direct512-output-token answer; summary helpers512 each plus final512;
fact-preserving helpers512 each plus final512; arithmetic-expression512 on FinQA.
Helpers return text, not executable Python. The arithmetic interpreter accepts
only numeric literals, parentheses and + - * / with finite bounds. All input,
output, helper and final calls are counted. These arms are NOT compute matched.

All model inputs are built only from question, documents, and actual helper
responses. Gold stays in host scoring. No gold support selection. No fallback
answer on failure. Missing responses are unavailable; malformed returned answers
are failures. Full inputs above24000 rendered tokens are excluded from every arm
before calls, with no truncation. This is an admissible-length LongBench screen,
not full LongBench performance. Numeric scoring uses supplied targets with1e-6
tolerance; string answers use article/punctuation/case normalization and aliases.
This lightweight exploratory metric is not claimed to reproduce every official
benchmark scorer. FinQA annotation/units caveats remain applicable.

Pilot16, next64, next176, next256 cases are fixed before outcomes. Larger blocks
require at least8available prior episodes with at least one success and one
failure in that model/dataset. A later block repeats the first80 cases with
four-way division and new seeds; it is not new-case evidence. No best-arm-only
reporting. Dataset-level gating makes this exploratory, not confirmatory.

## Run and monitor

Use the same frozen source and inputs for resume. Completed episodes and calls
are read from disk, not regenerated. An interrupted call may be attempted again,
with a separate start receipt so repeated physical work remains visible.

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python campaign_v3.py \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/unattended-breadth-20260914/outputs/campaign-001 \
  --hours 36
```

For detached execution use `python launch_detached.py` with the explicit Python
above; use `launch_detached.py --resume` after an interruption. It checks the
successful pilot, records its PID and enforces an external timeout. The command
above is the foreground equivalent. Version3 is the admitted owner; earlier
versions and failed pilots are preserved for provenance.

The owner takes the existing exclusive GPU flock. It uses at most36hours and
stops10minutes before the recorded SLURM allocation end, whichever is sooner.
It does not extend or request allocations. An all-transport-error batch stops
the current service; failures remain in summaries. Only this owner's process
group is terminated. Other sessions must not use the reserved GPU concurrently.

Read outputs/campaign-001/STATUS.json for live counts and per-arm scores,
SUMMARY.json for completed-stage summaries, and services/*/SCIENCE.json for
actual model-return counts. Raw requests/responses are in models/*/calls/ and
episode-level scores in models/*/episodes/. Service logs and private local
authentication files must never be committed. The full queue may finish before
the deadline; it will not manufacture filler experiments to occupy the GPU.

Create the empty file outputs/campaign-001/STOP to request a graceful stop.
Remove that exact stop marker only when intentionally resuming. The final
TERMINAL receipt and service RELEASED receipts distinguish finished jobs from
merely occupied GPU memory. A status file alone does not prove a process is live.

Source lives outside the repository to avoid changing the main RLM kernel.
Public snapshots exclude raw data, private service files, caches, and weights.
