# RLM research dossier

This dossier connects the research questions, completed experiments, evidence,
and next decisions. Its purpose is to make the work understandable without
requiring the reader to inspect thousands of run files.

**Status:** Complete for the evidence slice ending **2026-09-09 01:35 UTC**.
This edition catalogs 30 experiment families, 10 thematic findings, 24 structured claims
and five candidate comparisons, with 62 numbered sources. The newest controls are
read from primary aggregate files; their separately reported raw audit is explicitly
distinguished from a published audit artifact. Later original-weight scope and root
continuation outcomes are outside this edition. Raw runs and checkpoints remain
in their original locations; an unfinished comparison is not a measured effect.

## Where to start

Read [Overview](OVERVIEW.md) for the big picture, then
[Findings](FINDINGS.md) for the evidence organized by research question.
Read [Next experiments](NEXT_EXPERIMENTS.md) when deciding what to run.
Use the experiment catalog and source inventory to investigate a specific claim.

| Document | What it should help the reader understand |
|---|---|
| [Overview](OVERVIEW.md) | What we are trying to learn, what we know so far, and what remains uncertain. |
| [Findings](FINDINGS.md) | The salient results, their supporting experiments, and their implications. |
| [Experiment catalog](EXPERIMENTS.md) | What each experiment changed, what it measured, and where its artifacts live. |
| [Limitations](LIMITATIONS.md) | Conflicting results, alternative explanations, missing controls, and failed or unfinished work. |
| [Research questions](RESEARCH_QUESTIONS.md) | The living idea backlog, including which questions the evidence makes more or less promising. |
| [Next experiments](NEXT_EXPERIMENTS.md) | Ranked comparisons that can distinguish competing explanations on the available hardware. |
| [Sources](SOURCES.md) | Exact reports, manifests, datasets, and primary literature supporting the dossier. |
| [Decision history](DECISIONS.md) | Why recommendations changed and which questions are still open. |

Machine-readable companions, [Claims](../../../../ARTIFACTS.md#unpublished-files "Not published: CLAIMS.json") and
[Candidate queue](../../../../ARTIFACTS.md#unpublished-files "Not published: CANDIDATE_QUEUE.json"), connect findings, experiments, questions,
and proposed actions through stable identifiers. Identifiers are cross-references,
not substitutes for descriptive names.

[Source inventory](../../../../ARTIFACTS.md#unpublished-files "Not published: SOURCE_INVENTORY.json") records exact local paths and hashes.
[Verification](../../../../ARTIFACTS.md#unpublished-files "Not published: VERIFICATION.json") records source, link, cross-reference and selected
numerical checks. Candidate designs are not launch authorization or changes to the
live queue.

[Post-cutoff audit note](POST_CUTOFF.md) links the subsequently published independent
controls reconciliation without changing this edition's evidence slice.

## How to interpret the evidence

A finding should state the observation first, then its interpretation, then what
would strengthen or overturn that interpretation. A working hypothesis is not an
established explanation. Repeated predictions on the same source question are
not independent new questions. A successful child model is not automatically a
successful full RLM system.

The catalog keeps training, evaluation, implementation checks, and operational
failures distinct. It also separates completed results from pending work and
separates measurable wrong answers from missing outcomes. The source inventory
provides artifact paths and hashes for important quantitative claims.

## Terms used in this dossier

An **RLM** lets a language model use a Python environment to inspect an input,
divide work into smaller tasks, and call a model for help. The **harness** is the
software that gives the model those abilities and passes observations back to it.
The **root** model coordinates the task; a **child** model handles a delegated
task. The same underlying model can serve both roles.

**Supervised fine-tuning (SFT)** trains a model on example inputs and desired
outputs. **Training with checkable rewards (RLVR)** updates the model using
rewards determined by a program that checks an answer. A checkable final answer
does not necessarily prove that the intermediate reasoning or decomposition was
correct. These distinctions matter when interpreting our preliminary results.

## Scope and preservation

This is an additive analysis layer. It does not move or rewrite raw experiment
outputs, checkpoint files, frozen inputs, or earlier reports. Source paths remain
resolvable, and conflicting earlier interpretations are documented rather than
silently erased. The operational run queue is maintained separately in
[the live research queue](../../RESEARCH_QUEUE.md).
