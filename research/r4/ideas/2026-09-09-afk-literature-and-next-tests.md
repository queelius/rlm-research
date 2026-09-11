---
schema_version: rlm-literature-decision-v1
id: literature:2026-09-09-afk-update
reviewed_utc: "2026-09-09T18:57:16Z"
status: prospective_research_decisions
related_questions:
  - rq:correspondence
  - rq:controller
  - rq:sufficient-interface
sources:
  - url: "https://arxiv.org/html/2608.27038v1"
    title: "Cascaded Batch Prompting"
    submitted: "2026-08-27"
    reviewed_scope: "Method, experiments, costs, limitations and Appendix A text; prompt figures not inspected."
  - url: "https://arxiv.org/abs/2608.14737"
    title: "Class Imbalance and Batch Effects in LLM-Based Screening for Systematic Reviews"
    submitted: "2026-08-13"
    reviewed_scope: "Primary abstract only."
  - url: "https://arxiv.org/html/2608.02276v1"
    title: "Harness-R1"
    submitted: "2026-08-03"
    reviewed_scope: "Introduction, method, selected results and held-out-task protocol."
  - url: "https://arxiv.org/html/2606.14249v1"
    title: "HarnessX"
    submitted: "2026-06-12"
    reviewed_scope: "Introduction and cross-harness optimization sections; not a full implementation audit."
artifacts_acquired: false
new_gpu_jobs_authorized_by_this_note: false
---

# Research decisions from current evidence and recent papers

The useful unit of progress is a question resolved or narrowed, not a model file
or another training run. The current evidence suggests separating three links:
whether a child produces the right facts, whether the parent receives enough
information, and whether it actually uses that information to compute an answer.

## A recent batching paper is a relevant comparison

Hoshino and Zhang separate batched answer generation from conversion to final
answer symbols. Their experiments cover multiple-choice questions and natural
language inference; the benefit is not uniform across models and tasks. Their
implementation adds an individual symbol-conversion call for each item, not just
one extra batch call. They also distinguish missing-output alignment failures
from the primary uncorrected result. This is relevant prior work for any broad
claim that decomposing batch output generation improves reliability.
[Cascaded Batch Prompting, v1](https://arxiv.org/html/2608.27038v1).

Our narrower inference: source correspondence and answer-symbol conversion are
different possible bottlenecks. Our news and sentiment experiments already use
meaningful category names, yet their outputs respond strongly to source-linked
cues. The approved free-ID factorial tests whether that effect remains useful
without a grammar supplying the tags. It is not a replication of this paper.

If free IDs work, compare a one-stage source-linked answer with a two-stage
answer-then-symbol baseline on a separately frozen task. Count every conversion
call and preserve omissions; do not silently repair alignment or quote throughput
alone as cost. A first discriminator can use four 32-item contexts, paired seeds,
one released 4B model and a 45-minute outer cap. This is a proposed envelope,
not a ready experiment or measured duration. Promote only an advantage that
survives actual total-call/token accounting; otherwise retain the simpler method.

Hida and colleagues report that batching changes classification behavior in
systematic-review screening, with aggregate and item-level analyses sometimes
disagreeing. Only their primary abstract was reviewed here. It motivates retaining
paired item changes and class-specific mistakes, not importing their numerical
results or assuming their protocol matches ours.
[Class Imbalance and Batch Effects, v1](https://arxiv.org/abs/2608.14737).

## Co-adapting the harness and weights needs a narrower contribution

Harness-R1 trains a separate editor to propose executable harness changes from
failure traces. Its reward comes from rerunning a frozen target; its held-out
protocol derives a patch from a small failure set and evaluates other tasks.
HarnessX instead combines typed harness changes with training the task model on
trajectories collected under different harnesses. These are distinct approaches,
but both limit any claim that harness–weight co-adaptation itself is new.
[Harness-R1](https://arxiv.org/html/2608.02276v1),
[HarnessX](https://arxiv.org/html/2606.14249v1).

Our inference: a concrete contribution could concern which information an RLM
must preserve across a decomposition boundary, and whether a learned consumer
can use it across new partitions and query combinations. First compare fixed
interfaces and fixed weights; then cross trained/untrained consumers with old/new
interfaces. This separates an interface effect, a weight effect and their
interaction. A larger autonomous editor is premature while our small roots
often ignore an available map or repeat a generic worked example.

## Current decisions, with evidence gates

| Question | Smallest next comparison | Decision changed |
|---|---|---|
| Can useful IDs be freely emitted? | Approved 96-call free/exact-decoder × three-output-format test on the same exposed records and one released model; 1800s outer. | Distinguish a practical generation technique from a grammar-assisted component effect. |
| Does a generic example compete with current task evidence? | Approved 32-endpoint example present/absent × map file/inline test, fixed RL4 and actual child predictions; 1350s outer. | If removing the example or exposing the map restores calculation, repair the instruction/state interface before more root training. |
| Are child reports sufficient across different partitions? | Active fixed 88-call synthetic pilot with ordinary reports, full evidence, an explicitly lossy control and direct baselines; 1800s outer. | Increase difficulty if direct answers are near ceiling; address truncation before interpreting report omissions; train report choice only after a real content gap appears. |
| What should the next SFT targets teach? | Proposed matched corrective-action training at genuine map/error observations, with native executed reductions and disjoint query compositions. | Require a target that has meaningful remaining prediction error and improves held-out scoped calculation. Do not repeat saturated scalar-copy targets merely because training loss falls. |

The final SFT proposal still requires a frozen corpus, seed, optimizer budget and
resume/checkpoint policy. It is not launch-ready. Its motivation is the
[completed training audit](../operations/2026-09-09-allocation-5780/complete-sft-audit-report.md),
not a claim that a new correction method has worked. No paid external-model calls,
repository clone, dataset download, installation or published-code execution was
performed for this focused literature update. Ready GPU work continued throughout.
