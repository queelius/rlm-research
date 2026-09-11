# Related work that narrows our possible contribution

MAIN focused primary-source reading, September9,2026 16:39UTC. These are inputs
to current experiments, not a completed systematic literature review. No external
repository or dataset was downloaded for this note.

## Output decomposition and its cost

[Cascaded Batch Prompting, v1, August27,2026](https://arxiv.org/html/2608.27038v1)
separates batched label-name generation from a second symbol-mapping stage.
Its experiments include MMLU/MNLI and three models. It also discusses missing
batch outputs and explicitly excludes optional repairs from its main comparison.
The implementation uses N/b batched calls plus N individual grounding calls;
the reported gain is not a universally free batching improvement. This is related
decomposition work, not evidence that our record-ID cue is new or that semantic
errors can be repaired simply by reformatting them.

Experiment enabled: hold predicted semantic evidence fixed, compare its delivery
and exact executable aggregation. Our approved whole-RLM bridge instead changes
child generation while keeping broker delivery fixed; the two address different
boundaries. A later two-stage semantic/formatting comparison would need all calls
and token costs, unchanged primary failure accounting, and roughly20–30minutes
on one A100 for a24-task screen. Promote only if final correctness improves under
an explicit cost comparison, not from easier parsing alone.

## Repetition as a useful generation prefix is established prior work

[Echoes as Anchors, v1, February6,2026](https://arxiv.org/html/2602.06600v1)
studies repeated-question prefixes, likelihood comparisons, attention summaries,
echo-related SFT and inference prompting in reasoning tasks. It includes length-
and suffix-controlled analyses. Our source-ID results concern many record-label
correspondences rather than repeating one problem, but we must not claim that
useful repetition or generation-side reminders are newly discovered. Correlated
attention differences alone would not establish our causal mechanism.

Experiment enabled: approved local-cue replay holds all preceding output objects
fixed and changes only the current source cue. About288 candidate forwards on one
A100 within a900-second outer cap test whether a local effect survives shared
history. A positive effect narrows the account; disappearance suggests that full
generation history or other package differences matter. This is a conditional
likelihood diagnostic with supplied previous labels, not a sampled task result.
No code from the linked paper has been executed.

## Schemas are not just neutral output containers

[Your Prompt Is Not the Only Prompt, v1](https://arxiv.org/html/2608.08254v1)
compares definitions placed in prompts or schema descriptions, conflicting
definitions, and a required intermediate reasoning field on a small nonce-label
classification task. It reports model-dependent schema effects and explicitly
does not establish an internal mechanism. Its schema-description channel differs
from our controlled native prompt-token comparisons: our decoder can force output
tokens without rendering the differing schema into the physical prompt.

Experiment enabled: shifted72 separates positional label correctness from the
label belonging to a misleading forced source ID. All72 calls fit a900-second
outer cap on one A100. Named-source following would support a constrained cue-
following account; retained positional performance would weaken it. Neither
outcome establishes a new instruction-hierarchy phenomenon or hidden attention.

The promising publication direction remains a careful, bounded account of when
record-to-answer correspondence breaks, how cue timing affects it, and whether
that component benefit survives integration into a freely acting RLM. Generic
batching, IDs, output-field order, useful repetition and SFT-to-RL are prior art.
Our methods should make the narrower empirical contribution easy to evaluate.
