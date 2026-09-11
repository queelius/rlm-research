# Make the useful plan depend on the question

Exploratory proposal, September9,2026 at approximately06:50UTC. Not an accepted
GPU job and not a change to the running receipt study or prepared broad16 campaign.

## Why this should follow the present work

Two original-start root training seeds now have positive transfer-direction
readouts on exposed count tasks (the second is9/24 to15/24 under its fixed
checkpoint-selection rule). That motivates transfer tests, not an assertion that
the root has learned general adaptive decomposition. Broad16 is already being
prepared to vary source arrangements, lengths and requested categories.

There is a remaining limitation: labeling every record in batches of16 is a good
fixed plan for nearly every current question. More count-task training cannot by
itself show why a question-sensitive planner is useful. The sibling structured
decomposition benchmark's context-lens proposal makes this same headroom issue
explicit; see the earlier output-correspondence-and-context-lenses.md note.

## Falsifiable question

Can the root exploit inexpensive metadata filters when they are relevant, while
still gathering broad evidence when a question needs it? A useful policy should
retain final-answer accuracy and spend fewer child calls/tokens on selective
questions. It should not obtain cheap scores by guessing from missing evidence.

Keep question texts from a public, provenance-tracked classification corpus.
Give each record synthetic public user/date fields, assigned independently of its
semantic label. These are controlled task variables, not real personal information.
The leaf still supplies semantic categories; ordinary Python handles filters,
joins and aggregation. Keep host labels/gold answers out of the runtime.

Candidate question families on the same input:

- Count questions about numbers from one specified user. The root can filter
  user metadata before asking the helper to classify the surviving records.
- Count questions about numbers over the entire input. A user filter is invalid;
  evidence must cover the relevant source population.
- Count users who asked both a people question and a numbers question. This
  requires combining semantic evidence across records, not adding local counts.
- Find the earliest date with a specified semantic category. Sorting public dates
  and checking successive windows can permit early stopping; choosing a filter
  that excludes earlier unseen records is not valid evidence.

Examples must use complete, unambiguous sentences. Record exact gold computation,
tie/absence rules, metadata construction seed, answer prevalence, useful subset
size, and the oracle's record-inspection requirement as diagnostic metadata. An
oracle inspection count is not an attainable learned-policy guarantee. Fix the
metadata generator before examining model outcomes; do not cherry-pick easy tasks.

## Smallest useful comparison and resource shape

CPU preparation first: identify unused source groups from the existing frozen
split, exclude all named root training/validation/evaluation groups, and record
leaf-training exposure rather than calling the texts wholly unseen. Candidate:
eight128-record contexts with four question families and two seeds. Freeze the
actual count only after a source-membership audit; no speculative large download.

Compare a fixed classify-all-in16s program with a free root using the unchanged
Python/recursive environment. If useful weights exist, cross original and one
prespecified trained root with those questions. Use the same child checkpoint and
strict semantic classifier contract for the fixed program and root where their
requests coincide; document unavoidable prompt differences. Do not give the root
the oracle subset, planner labels or host gold. A later explicit filter helper
would be a separate harness intervention, not part of this baseline.

One A100, approximately45–90minutes for a bounded first screen, with a90-minute
cap if promoted; exact call/episode counts and measured prior runtimes will set
the final envelope. Save every episode and physical call. No new weight training
is needed for the first screen. Subsequent reward training is justified only if
the tasks show a genuine accuracy/cost tradeoff and different useful plans.

## Decisions this evidence can support

Promote adaptive training if roots solve enough examples to provide mixed rewards,
yet miss a meaningful accuracy/cost opportunity available to simple filtering.
Compare terminal reward with a separate, explicitly budgeted cost objective; do
not silently turn a decomposition preference into a correctness reward.

If classify-all remains best everywhere or almost all roots fail basic execution,
the first screen has not established a planning-learning target. Improve task
headroom or prerequisites rather than running a long adaptive-RL campaign by habit.
If the root already filters correctly, test new metadata/query compositions and
longer contexts before adding machinery. This proposal is lower launch priority
than the already ready receipt study and broader reward-training run.
