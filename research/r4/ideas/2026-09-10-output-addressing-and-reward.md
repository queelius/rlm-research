---
id: output-addressing-and-reward
status: literature_connected_exploration
created_utc: 2026-09-10T16:56:00Z
questions:
  - Can output order reduce misleading identifier interference?
  - Can address-specific rewards improve correspondence without rewarding copied labels?
  - When should the harness handle identifiers rather than asking the model to generate them?
---

# Treat the output interface as part of the harness

Our local MNLI experiments show that identical output-tag requirements can
produce very different semantic accuracy depending on which identifiers also
appear beside input text. Explicit same-record wording did not remove the
large penalty. The next queued experiment swaps label/tag generation order
while keeping the records and requested tags fixed. This idea was specified
before the following literature search; the sources refine its positioning,
not its now-frozen predictions or thresholds.

## Closest recent evidence

[Where vs What](https://arxiv.org/html/2608.25358v1), August26,2026, separates
format, required paths and correct value placement. MAIN read sections1–6,
limitations and training AppendixF. Its Qwen2.5-7B LoRA study uses GRPO with
reward VPA+0.3SCR, ten samples/prompt,500steps and fourA6000s. JSON placement
improves0.264→0.629 versus0.281 for best-of-ten SFT. Table-OOD placement is
0.094→0.085 despite much better formatting. Thus the abstract's broad
transfer story needs qualification. The SFT comparison also changes data
generation/update dynamics; do not repeat its assertion that only training
paradigm differs without checking compute and rollout budgets. No official
implementation link was identified in the inspected paper. Our three-class
labels are not unique planted markers: merely finding a label somewhere is
uninformative, so its value-presence diagnostic cannot be copied directly.

[Schema Key Wording](https://arxiv.org/html/2604.14862v1), April16,2026,
studies prompt versus generated-key instructions under constrained decoding.
MAIN read the abstract/introduction, formulation and inspected limitations;
the entire empirical section has not been reviewed. It establishes nearby
prior art for schema language influencing answers, not our specific
identifier-correspondence manipulation. Our proposed order change keeps the
field names and semantic category definitions constant; it must not be
presented as the first evidence that output formatting affects accuracy.

[Your Prompt Is Not the Only Prompt](https://arxiv.org/html/2608.08254v1),
August8,2026, compares definition placement and conflicting schema descriptions
in classification. MAIN read abstract/introduction and condition definitions;
the full results/code remain unreviewed. Adding a reasoning field is a
different intervention from swapping our answer and identifier. Its official
[evaluation repository](https://github.com/alina-lin-phd/prompt-placement-eval)
is an acquisition candidate, not installed or executed here. Schema text sent
to a proprietary model is also not automatically equivalent to our local
grammar-only constraint; record the actual native prompt in any comparison.

## Ranked experiments

1. **Ready and queued: output-field order48.** OneA100,1440-second cap,
   likely several minutes, eight exposed contexts, three reference conditions
   crossed with two field orders. Advance on a large aligned-referenced
   improvement across contexts without an availability loss; otherwise shift
   toward input simplification. Exact protocol lives in the sealed sidecar.
2. **Candidate: host-side identifier join.** Compare tag-bearing outputs with
   a label-only array joined to IDs by ordinary code. A48-call pilot on eight
   contexts fits the same oneA100 envelope. Measure semantic accuracy and
   complete cardinality; no silently repaired arrays. This tests a practical
   harness package, not a pure field-order mechanism.
3. **Candidate: correspondence-focused RLVR.** Use training-only premise
   groups, randomized identifier relationships, fresh zero-LoRA initialization
   or a declared fixed child checkpoint, and per-record correct-address label
   rewards. Compare terminal binary with dense fraction-correct rewards under
   equal rollout/update caps. Start with128–256 rollouts and4–8updates on one
   A100, checkpoint every update, then evaluate untouched groups plus larger
   batches. Estimate the wall cap using the actual short-batch rollout rate
   before committing to a longer run. Reject rewards for mere label presence
   or schema correctness when the decoder already guarantees the schema.

These are possible follow-ups, not claims of completed training or novel
algorithms. The immediate result to mine is the interaction between native
output requirements, competing visible identifiers and semantic correctness.
