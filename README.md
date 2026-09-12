# RLM research notebook

This repository makes the small, readable part of our recursive language model
research available outside the GPU cluster. It is a publication snapshot, not a
backup of the working filesystem and not a claim that every experiment succeeded.

Latest partial refresh: September 12, 2026, 17:42 UTC evidence cutoff. RL's earlier
gain repeats across two training seeds, but becomes smaller on fresh news examples:
427 and 429 correct out of 512, versus 422 before training and 426 after supervised
training. RL does not clearly beat supervised training on this fresh panel. The
earlier panel's 437 and 436 remain separate; the methods did not use equal compute.
This refresh preserves the weaker finding, complete four-arm audit and follow-up
decisions, not just the encouraging first result. Repeating the same 128 training
articles for eight updates reduced the earlier-panel score to 417/512, compared
with 437/512 using different article groups. This supports investigating data
variety; the repetition control still needs a fresh-panel check.

On 224 encyclopedia descriptions, the four models scored 209, 209, 208 and 210:
essentially unchanged. In the complete RLM, helper labels improved from 103 to
108 correct out of 128 distinct articles, but final answers stayed at 3/16.
Saved programs expose wrong counting scopes and calculations that returned no
visible value. Better intermediate labels do not guarantee a better final answer.

The controller investigation also changed our interpretation. Four nearly correct
conversation answers followed broad printing of the input, not correct Python
retrieval. We are testing explicit procedural demonstrations and partial-answer
rewards separately, while inspecting how the answer is obtained. The first root-RL
attempt stopped before any weight update because its probability weights were
too uneven; this is not a negative learning result. A small recursive-depth
comparison is running. A syntax-example interface variant reduced invalid actions
but worsened answers, and is being retired.
Infrastructure failures and GPU idle time remain visible.
Other records retain their earlier cutoffs; this is not live GPU status. The latest
plain-language synthesis is also in the
[September 12 research report](https://github.com/queelius/rlm/blob/main/docs/research-checkpoints/2026-09-12-broader-rl-learning-signal.md).

## Start here

- [Current findings in plain language](research/r4/analyses/NOW.md).
- [Longer experimental history](research/r4/analyses/CURRENT_SUMMARY.md).
- [The most promising findings](research/r4/analyses/PROMISING_RESULTS.md).
- [Research questions](research/r4/questions/README.md) and [supported claims](research/r4/claims/README.md).
- [Advisor slides, PDF, and presenter guide](https://github.com/queelius/rlm/tree/83cd0269da9774aa2280cc3d3f462178ea894bf9/slides/2026-09-11-advisor-meeting).
- [Complete snapshot index](INDEX.md), including earlier research rounds.

The central question is whether a small model can do more useful work by learning
to inspect a problem, ask smaller questions, and combine the answers correctly.
The notebook retains promising results, unsuccessful approaches, limitations,
corrections, and proposed next experiments. A proposal or a runnable script is
not evidence that an experiment was completed.

## How this fits together

| Location | Contents |
|---|---|
| [rlm](https://github.com/queelius/rlm) | Runtime code, tests, documentation, and presentation source. |
| This repository | Research questions, claim records, reports, ideas, experiment scripts, and compact evidence metadata. |
| Separate artifact storage | Large traces, datasets, model weights, and checkpoints; see [artifact availability](ARTIFACTS.md). |

The [source-repository record](SOURCE_REPOSITORIES.json) identifies the related
projects and their local commits when this snapshot was made. They provide code
or research ideas; their results must not be pooled without an explicit comparison.

## Read the evidence carefully

These are exploratory studies. Many tests reuse public source data or previously
examined contexts. Reports distinguish missing outcomes from observed failures,
correct final answers from actually performing the requested calculation, and
local improvements from improvements to a complete task.

The [manifest](MANIFEST.json) records original paths, file hashes, publication
paths, and any link rewriting. Original records were copied, not moved. Source
files and active GPU jobs were not changed by publication. This is a per-file
snapshot of a live research store, not a transactionally frozen experiment bundle.

Some scripts retain cluster-specific paths and depend on artifacts not included
here. This notebook is therefore not yet a one-command reproduction package.
Links to omitted local artifacts lead to the availability explanation; omitted
artifacts are not silently represented as publicly downloadable.

See [the publishing policy](PUBLISHING.md) for size limits, exclusions, and refresh
instructions. Third-party material retains its original rights and license;
publication here does not assign a new blanket license to datasets or imported code.
