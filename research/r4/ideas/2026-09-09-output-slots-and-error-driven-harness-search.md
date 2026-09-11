---
schema_version: rlm-literature-decision-v1
id: literature:2026-09-09-output-slots-and-harness-search
reviewed_utc: "2026-09-09T19:51:00Z"
status: prospective_not_ready
related_questions:
  - rq:correspondence
  - rq:controller
  - rq:sufficient-interface
sources:
  - url: "https://aclanthology.org/2026.findings-acl.1832.pdf"
    title: "Breaking the Autoregressive Chain: Hyper-Parallel Decoding for Efficient LLM-Based Attribute Value Extraction"
    published: "2026-07"
    reviewed_scope: "Abstract, introduction, method sections4.3/4.4 and selected experimental setup/cost text. Not all17 pages; figures not visually inspected."
  - url: "https://arxiv.org/html/2609.04197v1"
    title: "ESPO: Error-Structured Prompt Optimization via Diagnose, Diversify, and Stabilize"
    submitted: "2026-09-03"
    reviewed_scope: "Abstract, method3.1-3.4 and selected bootstrap/theory, ablation, cost and limitation sections. Not a reproduction or complete proof audit."
  - url: "https://arxiv.org/abs/2402.14811"
    title: "Fine-Tuning Enhances Existing Mechanisms: A Case Study on Entity Tracking"
    submitted: "2024-02-22"
    reviewed_scope: "Primary abstract and project landing page only."
acquired_manifest: "/project/alex_phd/research-cache/repos/HPD-5202217d90e921183d9a363f3663992241df37cc.PROVENANCE.json"
new_gpu_jobs_authorized_by_this_note: false
---

# Two useful directions, with limits on what we can claim

This is an additive literature/decision note, not a new result or a replacement
for the earlier [AFK literature snapshot](2026-09-09-afk-literature-and-next-tests.md).
Ready GPU studies continued while these sources were inspected. The ranked
[live queue](../RESEARCH_QUEUE.md), not this note, determines launch order.

## Can source-addressed output slots reduce the cost of a whole batch?

Hyper-Parallel Decoding generates values for known attribute slots by combining
position-ID gaps with a specialized attention mask and parallel token generation.
Its training matches the modified decoding arrangement. The logical causal mask
can expose earlier available value tokens to later slots; it is not simply a set
of completely isolated outputs. The paper studies attribute extraction and reports
efficiency improvements. Those are the authors' measurements, not estimates for
our A100 or evidence about recursive planning.
[Primary paper](https://aclanthology.org/2026.findings-acl.1832.pdf).

The paper's [official repository](https://github.com/networkslab/HPD) was cloned
read-only at commit `5202217d90e921183d9a363f3663992241df37cc`. At that exact
revision it contains only a170-byte README promising code later. There is no
implementation, dataset or repository license to reuse. The external acquisition
manifest records retrieval time, checksum, missing license and no execution.
No environment or model download was needed. Do not describe this as a replication.

Our proposed question is narrower: **can a model generate accurate source-linked
labels in parallel, lowering measured whole-batch cost without losing correspondence?**
An informative comparison would separate three changes: an explicit output
skeleton, the position/mask arrangement, and any training needed to use it.
Compare against ordinary autoregressive source-ID outputs, not only a weak
unaddressed array. Count every token/forward and report useful correct labels per
second as well as complete-batch validity; keep startup and peak memory visible.

Before spending GPU time, a paper-inspired implementation would need an explicit
mask specification, single-slot agreement with ordinary decoding, native
position/token records and a permissibly reusable implementation. A first pilot
could fit one cached4B model on this A100 with a45-minute outer cap, checkpointing
any training and retaining every planned output. This is only a proposed envelope.
Promote if whole-context quality and actual cost improve on disjoint inputs; revise
if gains come solely from the supplied skeleton; retire if implementation cost
displaces clearer tests of the already observed correspondence effect.

## Train a correspondence skill, or make the interface do the work?

Prakash and colleagues study entity tracking and report that fine-tuning improves
existing positional-tracking mechanisms in their models. This is relevant prior
work, not a mechanistic explanation of our behavioral ID-cue results; only the
abstract/project page was inspected.
[Primary abstract](https://arxiv.org/abs/2402.14811).

Our proposed next training contrast is matched SFT on source-ID versus control
outputs using the same disjoint training records and starting model. Then cross
both learned policies with free/exact output formats and longer unseen batches.
Use meaningful labels in both arms, retain source order, and separate ID validity
from semantic label accuracy. This asks whether learning transfers when the
training-time cue arrangement changes, or remains dependent on that arrangement.
It is not yet a frozen corpus, optimizer recipe or READY job. The completed
free-ID96 audit should determine whether this outranks a simpler whole-pipeline
comparison with the fixed parent and accurate environment descriptions.

## Search for harness changes from a complete error picture

ESPO groups training errors, proposes different kinds of prompt changes and uses
bootstrap-based candidate selection. It is useful prior art for error-driven
prompt search; this note does not adopt its reported gains or generalization
guarantees as established facts for our setting.
[Primary paper](https://arxiv.org/html/2609.04197v1).

Our statistical caution: resampling a fixed validation panel does not produce new
independent tasks or remove adaptive overfitting to that panel. More bootstrap
resamples improve Monte Carlo precision conditional on the observed panel, not
the amount of underlying evidence. Deterministic stored per-case outcomes can be
resampled on CPU; repeated model inference is not justified merely to increase
the number of bootstrap resamples.

For our harness, use the existing trace taxonomy to propose a small, diverse set:
remove a misleading example, make a field/map contract accurate, expose a compact
coverage summary, or change when detailed records become available. Fix each
candidate before its paired evaluation; retain all failures and costs. A useful
initial budget is at most four candidates on eight development contexts with one
fixed controller, capped45minutes on oneA100. Promote only a candidate that also
helps separately reserved contexts; do not repeatedly tune to the current four
map contexts and call that confirmation. The current clarity factorial is a
specific scientific comparison, not an autonomous prompt optimizer.

## Research decision now

Finish the already running clarity96 and accepted corrective-SFT comparison.
Use their native state-use and new-query readouts to decide whether the next
bottleneck is instructions, evidence gathering, combining evidence, or child
label quality. The partition final-interface pilot is a short independent backup.
Parallel output slots and learned correspondence remain ranked ideas, not an
excuse to delay those jobs or a claim that a novel system has already worked.
