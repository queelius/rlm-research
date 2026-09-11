# Three small harness experiments: preserve results, validate coverage, improve inspection

2026-09-09 UTC. Read-only design audit of the current core and exercised Prime/nano
sidecars. No core, frozen sidecar, campaign, model, service or dataset was changed.
These are proposals, not READY jobs. Source hashes are in the adjacent
`2026-09-09-core-harness-experiment-audit.sources.json`.

Recommendation: first test **direct commitment of an explicitly nominated computed
string**, using one shared computation prefix and paired terminal branches. It
isolates a demonstrated report-use/serialization failure cheaply. Do not implement
another core final-answer API: the core already has the required semantics.

## Existing capability versus the missing experiment layer

| Area | Core already implements | Exercised sidecar / remaining gap |
| --- | --- | --- |
| Child results | `ask_batch` preserves call order and full Responses objects; `AskBatchResult` identifies unusable text without silently retrying. Recursive helpers return full Responses objects. | This is transport/text validity, not within-answer record alignment, canonical labels or complete coverage. Nano returns `RLMResult.answer` text. Sidecar audits already reconstruct record coverage; the 8B generated controller explicitly validates its assignment map. |
| Final values | `FINAL_TEXT(str)` transports an already-computed string separately from bounded stdout; `FINAL_RESPONSE` submits a complete Responses object. Acceptance ends the branch without another model call. | Pinned nano ends on an assistant message without tool calls. Its Python result becomes a bounded observation and normally requires another model turn. No equivalent direct computed-value hook was found in that loop. |
| Inspection | Exact request in persistent Python state, metadata-only bootstrap, bounded observations, `SHOW_VARS`, configurable prompt policy. | `ContextSpec` currently selects latest-turn history/reasoning retention, not a sketch algorithm. MRCR already supplies complete read-only files and an optional deterministic context-only sketch. |
| Integration | `execution_factory`, separate controller backend and typed `ModelCallContext` role/depth already exist; harness/config snapshots are content-addressed. | Core's default IPython executor is **not sandboxed**, and its backend contract is Responses-only. Qualified sidecars use rootless nano, native TrainClient rendering and separate role-routing/token-capture overlays. They are not interchangeable runtimes or token traces. |

Core evidence: [ABI](https://github.com/queelius/rlm/blob/83cd0269da9774aa2280cc3d3f462178ea894bf9/src/rlm/abi.py),
[batch type](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm/src/rlm/types.py:251"),
[executor](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm/src/rlm/executor.py:604"),
[final handling](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm/src/rlm/engine.py:612"),
[context specification](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm/src/rlm/specs.py:119").
The ABI is closed and validates documented bindings; a new prebound helper cannot
be added while retaining the old ABI/digest. Ordinary research modules and task
renderers can be tried first. No generic plugin or new scheduling framework is needed.

## 1. Computed-string commitment versus final restatement

Question: how often does another generative final turn damage—or accidentally
correct—the answer the program actually chose?

Motivation: a recursive training positive computed `human being` but finally answered
`abbreviation`, matching gold despite the contradictory process. MRCR recovered a
correct full story but serialized literal backslash-n plus runaway padding. Conversely,
the 8B audit found faithful final aggregation in all 36 episodes: this intervention
has no demonstrated headroom on that saturated synthetic controller.
See [recursive audit](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/recursive-train-capture-v1/analyses/attempt-002/REPORT.md"),
[MRCR audit](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/mrcr-rootless-document-baseline-v2/analyses/attempt-001-accounting/REPORT.md")
and [8B audit](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/single-gpu-rlvr-8b-v3/analyses/attempt-001-root-worker/REPORT.md").

Small change: an additive container-local `submit_text(value: str)` helper and
structured REPL-result submission field, plus one nano loop termination branch.
Require explicit model invocation, a string, one submission and a successfully
completed cell; do not scrape stdout, infer a preferred variable, coerce arbitrary
objects, choose a gold-matching candidate or rewrite a historical answer. The REPL
serialization seam still needs a focused CPU qualification. Core needs **no final
API change**; its existing final semantics are the reference.

Smallest comparison: reuse the six MRCR documents as an explicitly developmental
mechanism replay, one fresh greedy computation per document, at most five shared
model turns before branching and six total including restatement. Before outcomes
are examined, define the nominated string to include the requested prefix and a
common explicit terminal-byte ceiling; reject oversize values, never truncate them.
At explicit submission, freeze that exact common prefix/value:
one branch commits the bytes; the other makes one native final restatement call
from the saved conversation. Report refusal/non-submission and tool-call responses
to that final-only request, without retry. This is six paired terminal results,
not twelve independently sampled full RLM trajectories.

Primary: candidate-to-final byte fidelity; secondary: official/exact score, direction
of score changes, final length stops, action/logical tokens and latency saved. A
correct commitment of a wrong candidate stays wrong. The comparison tests the
**runtime finalization contract**, not improved parsing, leaf semantics or planning.
Estimate: 5–15 minutes on one warm 4B A100, 20-minute cap; container overhead and
long tails dominate. If useful, a later full-trajectory off/on pair measures uptake
and any policy response to the interface.

## 2. Record-bound typed returns, with explicit coverage feedback

Question: can exposing structural validity prevent the root from losing usable child
work without pretending to verify semantic labels?

Motivation: full-RLM composition sometimes omitted questions or used placeholders;
one root extended an answer string character-by-character and returned zero despite
all 14 target records being correctly identified. The existing fixed scaffold did
much better, but changes many factors simultaneously. The
[integration audit](../analyses/leaf-role-composition-fixed-2026-09-08/REPORT.md)
separates those errors from actual label errors. This is **not** another batch-size,
index-prompt or rotation experiment.

Small change: a pure research module wraps existing child calls and retains the raw
answer plus caller-selected `(record_id, question)` entries. Only an exact-length
canonical-label array may be zipped to those caller IDs. Return `assignments`,
`expected_ids`, missing/duplicate/unexpected IDs and a structured validity result;
never truncate a long array, pad a short one, collapse label aliases or retry.
IDs are attached by the wrapper after checked alignment, so child prompts and
sampling can remain unchanged. This proves structural correspondence, **not that
the model semantically labeled the intended item**. Scope coverage is distinct:
the root can still select the wrong subset; scorer-only full-document coverage
must expose that error.

Pair 12 episodes: first three hash-ordered existing 64-record development composition
contexts, one preselected count target each, two fresh seeds, feedback off/on.
Freeze the original root and already-selected `c32de…` child, identical definitions,
unconstrained sampling and caller helper example. The control receives raw child
text; treatment receives the typed result. Validate both invisibly for analysis;
only treatment exposes diagnostics. Root recovery remains a model decision with
all subsequent calls charged. Record coverage, strict parse/cardinality, semantic
label accuracy, final/computed agreement, exact answer and cost separately.

This is a **return-representation plus policy-response** test, not a pure leaf-weight
or decoding-grammar test. Identical seeds do not guarantee identical root prefixes;
report that variation rather than attributing every pair difference to children.
Estimate: 10–25 minutes, 30-minute cap on one warm 4B A100. No core ABI change is
necessary for a research-module pilot; a generic registered helper merits promotion
only after an observable benefit beyond passive audit.

## 3. Question-aware offset sketches versus task-blind inspection hints

Question: does a bounded, query-relevant view help select the correct source response,
instead of anchoring the root on an irrelevant snippet?

Already present: MRCR's 4,096-byte sketch contains counts, frequent words and nine
uniform character samples. Complete context remains available. Both previous RLM
arms scored 0/6 exact; one sketch episode searched the unrelated flamingo fragment
it had seen while answering a space-riddle question. Native no-tools direct later
matched Chat direct byte-for-byte, 2/6 exact, so a new client explanation is not the
first target. [Paired failure report](../../../ARTIFACTS.md#unpublished-files "Not published: ../sidecars/mrcr-direct-six-v1/analyses/attempt-001-vs-native-rlm/REPORT.md").

Small change: a pure renderer first indexes **every** context-derived User/Assistant
boundary with character offsets. Compare uniform versus question-lexical-ranked
windows using the same index, renderer and 4,096-byte cap; expose total candidates
and omitted-window counts. Both arms include offsets and role boundaries, keeping
that improvement common. Ranking may read only the public question and document;
no answer field, gold offsets, parsed target occurrence or task-specific solver.
The model must still decide which matching occurrence and complete Assistant span
to read. No context truncation or automatic answer extraction.

Smallest comparison: six cached development documents, both first/second-occurrence
questions constructed from their public conversation instructions before scoring,
two views: 24 episodes. This makes the same context require different evidence;
freeze those question definitions and host-only gold before launch. Keep the
original 4B identity, native renderer, greedy full-support settings, six-turn limit
and 2,048-token call cap. Primary: correct occurrence/role/span selection and exact
answer; secondary: official score, irrelevant reads, syntax-error loops, final
truncation, logical/action tokens and wall time. Document is the grouping unit.

This tests **query-conditioned representation**, not learned adaptive inspection.
Only a later model-chosen `lookup_spans(terms, offset, limit)` versus fixed-query
schedule would test adaptation. Estimate: 10–25 minutes, 30-minute cap on one warm
4B A100; six short cached documents cannot support a long-context claim.

## Relation to the existing research program

The [bootstrap program](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm-bootstrap/docs/superpowers/specs/2026-08-28-adaptive-context-research-program-design.md")
already distinguishes executing a supplied plan from adapting inspection to context
and question. Its [integration contract](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/rlm-bootstrap/rlm_harness_integration_contract.md")
keeps weights fixed during harness comparisons and protects verifier, splits and
budgets. Apply that separation here; do not change campaign learning rules.

The [evolved-integrators roadmap](../../../ARTIFACTS.md#unpublished-files "Not published: /project/alex_phd/repos/evolved-integrators/docs/research/2026-08-25-program-search-roadmap.md")
supports restricted, inspectable candidates and charging every evaluation—not a
generic harness-search project before these three local operators show headroom.
Existing [cross-repository](2026-09-02-cross-repo-rlm-experiments.md) and
[primary-literature](2026-09-08-leaf-mechanism-literature.md) memos already distinguish
report truth from report use. External-context orchestration is established by
[Recursive Language Models](https://arxiv.org/abs/2512.24601v3), and typed functional
control by [λ-RLM](https://arxiv.org/abs/2603.20105v1). These are targeted adaptations,
not novel generic ideas or a claim to reproduce those papers.

All three retain raw failures and original metrics, host-only scoring, qualified
rootless execution and authenticated model/adapter/source identities. Complete
policy failures are not infrastructure failures. New helpers do not justify
relabeling old rewards or claiming on-policy trainability; that requires separately
verified native action masks/probabilities. The forthcoming campaign, batch-index/
rotation and sentiment-transfer work remain independent and untouched.
