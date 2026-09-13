# Completed research batch and resume handoff

Evidence cutoff: September 13, 2026, 01:00 UTC. All accepted GPU jobs and their
independent saved-output audits are complete. No model training or evaluation
is running in the background. The A100 is released and idle.

## What changed our next decision

Organized public records improved complete selection from1/24 to9/24 on twelve
fresh cases answered twice, while input fell52%. Gains occur in five cases,
all with six candidates. Larger cases remain incomplete; strict sorted answers
are0 versus2. Python retains every candidate and does not decide eligibility.
This is a promising hand-designed harness change, not learned recursion.

The stronger selection-RL update did not fix the task. Held graded reward rose,
but recall fell from79.1% to67.6%, with0/18 complete answers before and after.
Its local training score also fell. The smaller update's training advantage
disappears on common-valid ID-renamed comparisons; both models are name/token
sensitive. Stop repeating fixed-batch dose sweeps.

A narrow RL signal survived new conversations:24/32 to27/32 exact answers,
mostly better delivery of already-found information; clean retrieval29both.
FinQA adds a genuinely different task family but only weak evidence of useful
calculation prompting:2/16 targets matched versus1 direct on fresh pages.
The post-trained8B direct/perfect-helper diagnostic did not solve any of8
complete database tasks; it is not an isolated parameter-size comparison.

## Resume efficiently

Read SESSION_CHECKPOINT.md, analyses/NOW.md, RESEARCH_QUEUE.md and
questions/public-state-and-decision-accounting.md in the research store.
The leading ready-to-design comparison is an explicit yes/no decision for every
candidate versus the existing selected-ID list, with the SAME normalized input.
Then isolate resolved updates from shorter presentation, and only then train
varied selection decisions. These are proposals, not sealed or runnable jobs.

Exact inputs, seeds, runtime/model/template hashes, generated outputs, checkpoint
bindings, optimizer and RNG states remain in the external store. Selection
adapters are under sidecars/b05-flat-selection-rl{,-dose10}-v1/outputs/attempt-001/
checkpoint-0001/. Do not restart from a different initialization or silently
continue from the smaller-dose adapter. Read the matching READY.json and
EVAL_BINDING.json; current dual-LoRA serving uses runtime-an22-5801-v1.
MAIN is the sole GPU launcher and uses COORDINATOR.lock for every new job.

At01:03 UTC the supported main Codex account bucket had19% remaining. Optional
research is winding down, with pause15% and reserve10%. Reset is September19
08:09:56 UTC, not soon. The GPU allocation5801/an22 endsSeptember15 17:30:16 UTC.
Check both live on resumption; the user has another session sharing the quota.
GPU time remains, but budget reserve must not be consumed by filler or an
unbounded new experiment branch. The resulting GPU idle time is recorded.

## Publication boundary

The latest plain-language report is in the RLM repository:
docs/research-checkpoints/2026-09-13-from-answer-delivery-to-information-selection.md.
The historical meeting deck remains unchanged. This completed-result checkpoint
publishes compact source and selected audit evidence to the research notebook,
not private model inputs, raw financial/conversation traces, weights or environments.
The per-file5MiB limit stays; total snapshot budget becomes96MiB to retain the
new evidence without deleting earlier negative findings. Source hashes, read
times and link rewrites remain in MANIFEST.json.

Previous verified remotes at report preparation were RLM84e5b84 and notebook
e940231. A separate PUSH_RECEIPT.json will record the newly verified remote heads
after successful ordinary pushes. Do not mistake this source snapshot for a
backup of /project/alex_phd or the model checkpoints.
