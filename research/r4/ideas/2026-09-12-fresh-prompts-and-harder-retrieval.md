---
schema: research-question-v1
created_utc: 2026-09-12T21:18:00Z
status: exploratory_preparation
priority: high
questions:
  - Can new contexts restore useful RL feedback without weakening the trained controller?
  - Does the learned retrieval routine handle third and fourth matching requests?
---

# Change the examples before increasing randomness again

The competent checkpoint produced 28/32 exact answers at temperature 0.5 but
zero mixed-reward groups. Temperature 1.0 produced 27/32 with only one mixed
group, caused by a procedure failure rather than alternative copies of the
same retrieved text. Stopping SFT earlier produced more mixed groups but only
6/31 available exact answers. These results argue against another temperature
sweep on the same eight familiar questions.

The immediate follow-on uses eight previously unused short conversations in
frozen hash order, excluding exact core/target overlap with earlier panels.
Four attempts per new context at the competent checkpoint and temperature
0.5 keep sampling conditions unchanged. Count mixed groups, correct retrieval,
exact delivery and actual native token costs. Save all outcomes, including
unavailable ones; do not silently keep sampling until a favorable batch appears.
This is a training-data screen, not a heldout accuracy claim. Proposed shape:
one A100, 32 episodes, approximately 7–10 minutes including startup; science
cap 900 seconds. A new informative batch can support a separately admitted
group-relative update. Another all-equal batch would favor the fixed-baseline
objective or different task construction, not repeated resampling.

## A separate transfer question

Our demonstrated length transfer still uses the two-needle MRCR task family.
Acquire the official four-needle files at the same pinned dataset revision,
then prepare an outcome-blind panel that asks for the third or fourth matching
request. This probes a different ordering requirement, not merely more text.
It remains same-family transfer, not a new benchmark or proof of general
decomposition. Before a GPU comparison, freeze length bounds, ordinal balance,
exact-core/target exclusions, source hashes, question/answer validation and
all skipped rows. Compare fixed controllers, not an outcome-selected model.
Expected next screen: 16 contexts, base versus fixed SFT32 (and RL endpoint
only under a separately fixed comparison), about 8–12 A100 minutes for two
arms, with every native call checkpointed. Acquisition itself uses CPU only
and is capped at 600 MiB. No four-needle model outcome exists yet.

## Primary research informing the decision

[DAPO, v1](https://arxiv.org/html/2503.14476v1), section 3.2, already addresses
zero-advantage groups by oversampling and filtering groups with uniform
outcomes. Our observed zero-contrast problem is therefore not a novel discovery.
Its published compute setting is much larger than this pilot. Here we will
first measure whether a fixed, small new-context batch changes feedback,
rather than adopting unbounded sampling. Filtering changes which examples
enter an update; we must keep the full acquisition ledger.

[Learning from Hard Prompts, v1](https://arxiv.org/html/2608.27982v1), posted
August 28, 2026, proposes amplifying successful responses from difficult
mixed-reward groups after dynamic sampling. Its theory and experiments concern
that selected-group setting and mathematical reasoning. This does not repair
our uniform groups: scaling an existing zero advantage still gives zero.
Keep positive/negative credit balance as a later comparison if new contexts
provide genuine contrast. We have not reproduced its reported gains or
implemented its objective.

The [official MRCR card at the pinned revision](https://huggingface.co/datasets/openai/mrcr/blob/f4c69fae7cf81f7ca26b9fee34b392a50f6b8a1d/README.md)
describes ordering among similar requests and releases different needle counts.
Its December 2025 changelog reports corrections to generated examples; retain
the revision and validate the selected target relationships, rather than mix
older downloads with this source. No acquired third-party code is executed.
