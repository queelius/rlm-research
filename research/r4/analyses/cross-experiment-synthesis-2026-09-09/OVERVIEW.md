# Better parts do not yet make a reliably better RLM

The central research question is whether a model can learn to inspect an input, delegate the right pieces, and use the returned evidence more reliably or cheaply than answering directly. The strongest results so far concern individual parts of that process. The evidence for a broadly improved, learned end-to-end system remains weak.

Three results matter most.

1. **A small child model can be taught the intended classification task.** Supervised training raised strict TREC test accuracy from 355/489 to 473/489. That is not entirely a semantic gain: itemwise canonical accuracy rose from 374/489, and the strict score also rewards repairing invalid arrays. With fixed five-item batching and Python aggregation, the trained child raised exact aggregate answers from 1/24 to 15/24. With a freely acting root, the corresponding new-context comparison rose only from 4/24 to 6/24. The local skill is real; reliably using it is a separate problem. [F1–F2][^1][^2]

2. **Valid output is not the same as keeping answers attached to inputs.** The old five-item-trained child produced 24/24 valid 64-label arrays under a schema but zero correct aggregate answers. All questions reached the model; accuracy collapsed after the first 16 positions. The new representation control is more promising than simply training on longer batches: on a different, reused validation slice, anonymous arrays scored 181/512 labels, indexed output 405/512 and question-echo output 419/512. This changes representation and constraints, not just indexing. Mixed training improved some aligned labels but did not solve correspondence, and SST-2 showed no large generic rescue. [F3][^3][^4][^46]

3. **Root-only RLVR has run correctly, but a learning benefit has not been established.** A one-step pilot scored 2/8 before and 2/8 after; an unchanged-weight replay scored 4/8. A fresh campaign committed three persistent-Adam updates, with validation moving from 2/8 to 3/8 at step two. It stopped before step four because an authenticated, recovered overlong child request was classified as a fatal integrity error. There was no selected final checkpoint or new-context transfer evaluation. Neither “RLVR works” nor “RLVR cannot work” follows. [F5–F6][^5][^6][^7]

The earlier synthetic studies provide a useful positive boundary: supervised controllers can follow a taught adaptive routine and reduce conditional child-input tokens by 67.8%, while preserving or improving answers in that narrow setting. They do not establish strategy discovery or transfer to unfamiliar documents. Conversely, report-binding experiments in the neighboring decomposition benchmark show that making a root obey reports can improve report use while making wrong reports more damaging. The useful question is not merely whether decomposition happened, but whether its information was correct, used faithfully, and worth its cost. [F4, F8][^19][^28][^30]

The most promising research direction is therefore **evidence-faithful model–harness co-adaptation**: separately measure semantic competence, input/output correspondence, root consumption, final submission, and resource use; then train or change the one component whose intervention actually repairs an observed failure. This is a research recommendation, not an established mechanism or a novelty claim.

Read [Findings](FINDINGS.md) for the reasoning and counterevidence, [Limitations](LIMITATIONS.md) for what the numbers cannot establish, and [Next experiments](NEXT_EXPERIMENTS.md) for bounded comparisons. Completed controls are distinguished from pending work; interrupted or unrun experiments are never counted as successful results.

[^1]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^2]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^3]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^4]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^5]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^6]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^7]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^19]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^28]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^30]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
[^46]: ../../../../ARTIFACTS.md#unpublished-files "Not published: [Source"
