---
schema: rlm-literature-to-experiment-note-v1
id: "idea:visible-memory-and-credit"
updated_utc: "2026-09-10T10:17:00Z"
status: ranked_followup_not_implemented
question_ids: ["rq:sufficient-interface", "rq:controller"]
related_claims: ["claim:retention-is-not-completed-computation", "claim:procedural-card-headroom"]
primary_sources:
  - {url: "https://arxiv.org/html/2606.31650v1", scope: "MAIN methods, setup, limitations and selected official code; not all figure pixels or prompts"}
  - {url: "https://arxiv.org/html/2606.30005v2", scope: "MAIN core methods, selected experiments, ablations and theoretical assumptions; not a complete appendix audit"}
acquired_repo:
  url: "https://github.com/xiezijun714-lang/Echo"
  commit: "33370aa007c66c4294493ff5aa7ba3293dcc0da3"
  receipt: "/project/alex_phd/research-cache/echo-source.F0pWPo/ACQUISITION.json"
  execution: none
novelty_claim: none_established
---

# Separate keeping evidence, displaying it and rewarding its use

Our completed memory test retained real child answers in growing maps, but did
not elicit a completed multi-batch calculation. Some root requests exceeded the
context limit. This warrants the small display-budget test already in preparation;
it does not yet warrant a larger memory-and-training package.

## What the recent primary sources contribute

ECHO makes an agent record short findings and later select earlier turn IDs for
retention. Its reward update credits selected source actions, findings, selection
actions and the last segment. Importantly, the inspected implementation also
clamps group advantages to positive values in this mode; its dense baseline uses
signed advantages. That comparison therefore does not isolate the credit mask.
The reported setup uses 32 GPUs, long browsing trajectories and an LLM judge,
unlike our one-GPU, exact-integer task. Selected source code has a dense-credit
fallback when trace metadata is missing. We acquired the official source for
inspection but did not run it. These are design leads, not a replication.
[Paper and method](https://arxiv.org/html/2606.31650v1),
[pinned official source](https://github.com/xiezijun714-lang/Echo/tree/33370aa007c66c4294493ff5aa7ba3293dcc0da3).

VISTA distinguishes visible, archived and blocked context, with a dashboard and
file-backed recovery. It also changes admission: oversized results can be held
out, and normal actions can be disabled during overflow. Those controls matter
when interpreting its gains. The recoverability argument assumes suitable
handles and a correct recovery policy; it is not a guarantee that an actual
model will recover or use the right information. Its tasks and timeouts vary,
and not every benchmark favors the full system. It suggests testing a small
state receipt, not treating its entire interface as a passive-memory intervention.
No official repository was verified or acquired for this paper.
[Paper, methods and limitations](https://arxiv.org/html/2606.30005v2).

## Ranked experiments enabled by these ideas

First finish the already-defined batch/cumulative by ordinary/bounded-view test.
It keeps the model and underlying Python state fixed, preserves all planned
failures, and provides no calculation instructions. This is the cheapest way to
ask whether repeated display is preventing use of retained information.

If clipping improves availability but the model still does not use its retained
answers, test a factual receipt next: the count of decoded records, retained
record IDs or an ordinary variable reference, and displayed versus retained byte
counts. Freeze the exact receipt fields. Cross receipt absent/present with the
winning display configuration on fresh paired seeds. No task-aware category
totals, correct labels, code reducer or forced child call may be hidden inside
the receipt. Start with 32 endpoints on one A100, an 1,800-second outer cap,
four workers and per-episode traces. A stronger result must include faithful
calculation and stopping, not only a larger map or better availability. If the
receipt is ignored, revise selection training rather than rerunning it unchanged.

Only after a recoverable state interface produces a useful learning signal,
consider a small root-action credit experiment. Hold task samples, verifier,
advantage sign, optimizer settings, final checkpoint rule and compute cap fixed.
Compare all current root-action tokens with an explicitly defined retained-source
mask; include every attempted trajectory and account for mask construction cost.
The first pilot should be at most four 24-attempt windows and one paired readout,
under a three-hour outer cap on one A100. No hidden dense fallback or new judge.
Missing provenance must remain explicit. This is not yet queued for GPU launch:
our current tasks do not establish that such a mask identifies causally useful
actions, and selected evidence is not automatically necessary evidence.

These are our proposed comparisons, inferred from the papers and our traces.
They are not claimed contributions of either paper, and a borrowed component
is not itself a novelty claim. Record the evidence that promotes, revises or
retires each lever before combining model training and harness changes.
