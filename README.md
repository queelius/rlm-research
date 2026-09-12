# RLM research notebook

This repository makes the small, readable part of our recursive language model
research available outside the GPU cluster. It is a publication snapshot, not a
backup of the working filesystem and not a claim that every experiment succeeded.

Latest partial refresh: September 12, 2026, 21:00 UTC evidence cutoff.
Supervised training on 32 worked examples taught the controller to retrieve
the requested reply from a Python-accessible conversation. On 16 separate
conversations with two trials each, exact returned answers rose from 2 to 17.
The starting model completed 29 of 32 attempts; the trained model completed all
32. Among the 29 available pairs, training corrected 15 answers and lost none.
This is exploratory transfer within one task family, not general decomposition.

The fixed trained model also answered 10/16 new, longer conversations exactly,
versus 0/16 for the starting model. It retrieved the right text in 15/16 cases;
five final answers omitted two required spaces and one program searched for
the wrong request type. All outcomes were available. These new conversations
exclude exact core/target overlap with the earlier 48 records, but remain in
the same retrieval task family. The model accessed their text through Python,
not through an expanded neural context window.

The trained model printed the right text in 30 of 32 attempts. In eight cases
it also generated the exact final answer, but the runtime removed trailing
spaces before grading it. The original 17 successes remain unchanged. A new
run with both terminal whitespace operations disabled scored 23/32: seven
improvements and one regression. All seven improvements had identical model
token paths and recovered previously damaged answers. The regression had a
different final generation. A separate earlier token-level diagnostic found
25; it was not the result of this intervention. This is a harness improvement,
not RL, and the panel contains 16 contexts with two attempts each.

RL is not yet the strong result: the first controller evaluation found zero
exact answers before training, zero after the smaller update, and one after the
larger update, each with 15 available attempts. A second decoding block gave
2/15, 1/16, and 1/16 respectively. The small apparent advantage did not persist;
successes followed broad input dumps, not learned retrieval. Fresh attempts
from the competent supervised controller answered 28/32 exactly, but every
question had the same reward across four attempts. That gives group-relative
RL zero learning signal. An earlier checkpoint restored some reward variation
but answered only 6/31 available attempts, with one additional unknown outcome.
We are testing higher temperature and preparing a different fixed-baseline
reward objective; neither is yet an RL improvement result.
On another dataset, focused helper follow-up questions, broad
follow-ups, and stopping each answered the same one of 12 questions correctly;
reading the full source answered three. Another comparison held selected
passages fixed: summaries answered 4/12 questions and original passages 3/12.
It does not establish a general advantage for either representation; the
strategies also have different natural costs. Source-selection and answer-use
analysis is ongoing. Flexible allocation of four passages across the helpers
increased complete annotated-source coverage from 3/12 to 6/12, but both
policies still answered 3/12 exactly. It used an extra planning call. More
available evidence did not automatically mean the model combined it correctly.

Earlier helper-training claims are also qualified. On fresh news examples,
varied-data RL scored 427/429 out of 512, repeated-data RL 425, supervised
training 426, and the starting model 422. The earlier 20-answer advantage of
variety shrank to two on this panel. Better helper labels also failed to improve
whole-system answers. The notebook preserves these weakened findings and
unsuccessful comparisons alongside the promising procedure result.

Other records retain their earlier cutoffs; this is not live GPU status. The latest
plain-language synthesis is also in the
[September 12 length-transfer and reward-contrast report](https://github.com/queelius/rlm/blob/main/docs/research-checkpoints/2026-09-12-length-transfer-and-reward-contrast.md).

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
