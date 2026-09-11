# Separate understanding a small item from completing a long answer

September9,2026. Ranked exploratory followups; these do not modify running or
sealed experiments. Completed local evidence is in
[the mixed-size report](../analyses/mixed-size-prefix-diagnostic/REPORT.md).

## Primary literature that changes the questions

[How Focused Are LLMs?,v2](https://arxiv.org/html/2511.00763v2) reports abrupt
sequence-accuracy decline on repeated deterministic operations, despite inputs
fitting in context. It proposes a correlated-error model; that is not direct
causal evidence about attention inside our4B model. Importantly, v2 adds actual
divide-and-conquer experiments on Pauli strings and explicitly includes
segmentation/combination overhead. Thus neither an accuracy cliff nor improvement
from splitting is novel by itself. Our count accuracy permits error cancellation,
unlike their all-correct sequence endpoint; do not fit their scaling law to our
few batch-size/count results or treat it as established for this task.

[Exploring Limitations of LLM Capabilities with Multi-Problem Evaluation](https://aclanthology.org/2025.insights-1.12/)
finds that composing classification with index selection can be much harder than
ordinary batched classification. This matters for interpreting our record-ID
intervention: richer structure may aid correspondence but also add a skill demand.
Keep completeness, label accuracy and selection accuracy separate, and do not
call any improved indexed prompt a pure formatting effect.

[Hyper-Parallel Decoding](https://aclanthology.org/2026.findings-acl.1832/),published
July2026, generates conditionally independent attribute values with manipulated
position IDs and shared computation. It suggests a backend-level route to separate
independent output chains. Its reported extraction speedups are not measurements
on our task, model or serving stack. The official repository is linked by the paper;
we have not cloned or executed it. This is lower priority than cheap prompt/runtime
tests because it may require a different decoding implementation.

Three PDFs,5,320,783bytes, are pinned with URL/version/date/license status/SHA256 in
`/project/alex_phd/research-cache/2026-09-09-literature/output-correspondence-zQ5Yb6/SOURCES.json`.
No new benchmark or third-party executable was downloaded by this acquisition.

## Ranked next experiments

1. **Already queued/preparing: contract, correspondence and exact-template controls.**
   Use the four frozen checkpoints and exact existing source groups. First learn
   whether64-item training helps once cardinality is controlled, whether explicit
   record binding changes correspondence, and whether serializer order changes
   the result. Each failure stays in its original primary endpoint. Run this
   before claiming the model needs more training or a larger architecture.
2. **Next candidate: hold requested output small while varying visible context.**
   On four64-item development contexts, compare full64 output, four targeted16-item
   outputs retaining all64 inputs, and four16-item outputs with only the selected
   input window. Two seeds would require72calls on one warm frozen child. Use
   identical public target-ID instructions and explicit target boundaries in the
   two targeted conditions; no gold-dependent selection. Freeze the actual rendering
   before execution, use exact output cardinality, and retain failed target selection.
   Estimate5–15GPUminutes,20-minute cap; every call checkpointed. If targeted answers
   remain accurate at late input positions, that supports output-chain/selection
   scope as a bottleneck rather than inaccessible late input. If full-context
   targeted calls remain poor but local windows work, context distraction becomes
   more plausible. Neither result alone proves an internal attention mechanism.
   Charge all four calls; this is not a free accuracy improvement.
3. **Later candidate: conditional parallel outputs.** Inspect the official HPD
   implementation before any execution. The smallest informative comparison is a
   single existing checkpoint on the same task/source split with ordinary versus
   independent output streams, measuring exact coverage, accuracy, actual GPU time
   and cache use. CPU feasibility first, then one A100 with a60-minute cap if ready.
   Retire if incompatible kernels/setup exceed the value of the information; do
   not displace a ready training job or describe API batching as HPD.

## Connection to adaptive RLM research

The sibling [context-lens question](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/structured-decomposition-benchmark/experiments/rq-005-context-lens/README.md")
already proposes local-shard versus full-root worker context. Its
[primary study](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/structured-decomposition-benchmark/RESEARCH_QUESTION.md")
requires evidence of a consequential decision, observable predictors and headroom
over fixed rules before learned routing. We should adopt that reasoning, not its
entire infrastructure or a sealed evaluation set. No sibling code was executed.

These experiments currently measure a worker's useful operating range. Adaptive
decomposition needs another ingredient: contexts/questions where different choices
really are best. A uniform classification task on which fixed16 always wins offers
little reason to train a sophisticated router. Future data should vary whether the
query needs local independent facts or relationships across records, using the same
context with different questions and a matched-compute direct/fixed-plan baseline.
Only then ask whether an RLM can inspect the available context, select a useful
representation and choose the right subproblem scope. That is a stronger connection
to rlm-bootstrap than demonstrating yet another fixed-batching gain.
