---
schema: rlm-completed-result-v1
created_utc: "2026-09-12T12:02:00Z"
question_id: rq:rl-effective-feedback
status: qualified_exploratory_null_endpoint_comparison
report_json_sha256: d6d2d8d42ab158aeaf990d6632391f760eab5b6c63e5e0c1890fbf469222c308
---

# More nonzero feedback did not change the evaluated answers

## What we tried

We started two helper models from exactly the same supervised weights and
trained each once on exactly the same128 sampled answers to32 questions.
The only intended difference was how we calculated the reward baseline.

The ordinary calculation compares an answer with the other attempts at that
same question. A question receives no signal when all attempts are equally
right or equally wrong. The alternative compares an answer with the average
reward on the other31 questions. It can therefore give nonzero signal even
when a question's own attempts all receive the same reward. It does not supply
the correct answer, and more nonzero signal need not be useful signal.

| Observation | Same-question comparison | Other-question comparison |
|---|---:|---:|
| Training questions with nonzero signal | 5/32 | 32/32 |
| Optimizer updates | 1 | 1 |
| Correct question categories | 120/128 | 120/128 |
| Correct news categories | 112/128 | 112/128 |
| Unavailable evaluation answers | 0/256 | 0/256 |

Every one of the256 evaluation labels matched across the two models. They
also match the earlier four-update reference. Relative to the supervised
starting helper, each corrects the same single question-category answer.

## What this tells us

This particular way of recovering discarded feedback did not improve the
evaluated answers after one update. The updates were real and different:
both moved the adapter about0.04046 in parameter-space L2 norm, but their
directions had cosine similarity0.8389 and their endpoints were0.02297 apart.
That is parameter evidence, not a claim about how far their output
probability distributions moved. Identical greedy answers do not imply
identical probabilities.

Together with the higher-temperature and larger-update comparisons, this
lowers the priority of further small variations on the same32-question
training set. Next test broader task-relevant examples and root procedures,
with the already queued single-item serving check as a remaining diagnostic.
There is still no meaningful new RL quality gain to promote.

## Scope and cost

Both branches restored identical weights, all RNG domains and empty AdamW
state. All128 unchanged-policy action replays qualified for each branch;
the completed model bindings and source reuse were rechecked after evaluation.
The panel is disjoint from verified fine-tuning inputs but has been repeatedly
examined during this research. This is one batch, seed and update size, not a
general verdict on reward baselines or RL.

The original collection failed before training and was retained. Recovery
reused its exact128 actions, adding **zero newly sampled actions**. The failed
source attempt took288.134s, the recovery trainer1252.394s (wrapper1264.614s),
and the two evaluation owners112.261s and112.675s. These are separate costs;
the two branches do not represent256 unique training examples.

Accounting correction: legacy `arms/paired_*.json` calls its128 retained action
rows `training.fresh_actions`. For this repair that field is not a count of
new samples. The authoritative corrected accounting is in `REPORT.json`, under
`collection_accounting`, and the earlier `WATCH_SOURCE.json` records the reuse.

Evaluation decoding, requested-ID order, request-body hashes, usage metadata
and served adapter bindings were checked. The legacy evaluator did not save
full HTTP envelopes; those bytes cannot be reconstructed from response hashes.
Training has the stronger exact action/mask/RNG/replay provenance. No missing
envelope is claimed to have been independently inspected.

Machine-readable evidence: `REPORT.json`, `arms/paired_rloo.json`,
`arms/paired_other31.json`, and
`comparisons/paired_rloo__paired_other31.json`. The fixed256 source analyzer is
unchanged; `finalize.py` adds full branch qualification and tensor geometry.
