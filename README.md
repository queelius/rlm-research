# RLM research notebook

This repository makes the small, readable part of our recursive language model
research available outside the GPU cluster. It is a publication snapshot, not a
backup of the working filesystem and not a claim that every experiment succeeded.

Latest partial refresh: September 12, 2026, 22:16 UTC evidence cutoff.

Supervised training on 32 worked examples taught a small controller to find a
requested reply in a conversation through Python. Its routine transfers within
that task family: on separate panels, exact answers improved from 0/16 to 10/16
for longer conversations, and from 0/16 to 10/16 when the question asked for the
third or fourth occurrence rather than the first or second. Every outcome in
these comparisons was available. This is useful procedure transfer, not yet
general problem decomposition or learned recursive delegation.

We also found a concrete system defect: the answer path removed spaces that
the copying task required. Disabling that behavior recovered seven identical
generated answers. The paired score rose from 17/32 to 23/32, including one
separate generation-path regression. This is a harness correction, not RL.

The latest RL gain did not replicate. One final-answer reward update initially
raised short exact answers from 23/32 to 25/32. Running both fixed models again
with new decoding seeds reversed the result: 25/32 to 22/32, with three losses
and no gains. The losses added a final line break after correct retrieval.
These blocks reuse 16 conversations; extra seeds are not independent tasks.
We retain both blocks and do not present the favorable one as an established
improvement. A new mixed-reward training batch has produced a completed update,
but its accuracy readout is beyond this checkpoint's cutoff.

Extra helpers have not yet established better composition. On 12 multi-document
questions, extracting quoted relations and simply asking the final model for a
concise answer each raised exact scores from 3/12 to 5/12, but corrected different
questions. The gains changed wording of facts already present. The cheaper
instruction used fewer model calls; neither fixed missing evidence or reliably
assigned facts to the correct person. We are preparing a task with checkable
intermediate answers to study that distinction more directly.

Earlier helper-training gains also weakened on new examples and did not improve
whole-system answers. The notebook preserves those results, failures and
interpretation changes alongside promising findings. Records retain their named
cutoffs; this is not live GPU status. See the
[latest plain-language research checkpoint](https://github.com/queelius/rlm/blob/main/docs/research-checkpoints/2026-09-12-small-rl-signal-and-helper-controls.md)
for methods, limitations and evidence pointers.

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
