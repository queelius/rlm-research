---
question_id: adaptive_decomposition
status: completed_exploratory_screen_no_delegation_observed
evidence_date: 2026-09-12
primary_audit_sha256: 99ce1cc01229a67d175f7b2940ef0415562526f6890fcb4385b4bca6f7396170
unique_questions: 12
scheduled_episodes: 48
available_episodes: 47
physical_model_calls: 112
child_calls: 0
optimizer_steps: 0
publication_readiness: mechanism_diagnostic_not_positive_recursion_result
---

# Allowing deeper calls did not make the model delegate

We tested twelve MuSiQue questions that require connecting two to four facts.
For each question, the small model could use Python to inspect the supplied
paragraphs. Three conditions allowed no helper calls, helpers, or helpers that
could themselves call helpers. Each condition had the same six-call ceiling.
A fourth condition saw only the question, without its supporting paragraphs.

| Condition | Correct | Wrong | Unavailable | Questions |
|---|---:|---:|---:|---:|
| Python, no helpers allowed | 2 | 10 | 0 | 12 |
| Helpers allowed | 0 | 12 | 0 | 12 |
| Helpers of helpers allowed | 1 | 10 | 1 | 12 |
| Question only | 0 | 12 | 0 | 12 |

These numbers do **not** show that recursion is ineffective. The model made
no helper calls in any condition. All 112 physical model calls were root calls.
The experiment instead shows that merely making recursion available does not
teach this starting model when or how to use it. The conditions also change
the model's instructions, so differences among root-only trajectories are not
an isolated effect of actually delegating work.

## A concrete obstacle: the model searched the container, not its text

Several saved programs mishandled the input representation. A paragraph was
a dictionary containing fields such as its text. This simplified example
captures an actual mistake:

```python
for paragraph in paragraphs:
    if "Gong Beibi" in paragraph:
        matches.append(paragraph)
```

For a dictionary, that condition searches its **field names**, not the words
in its text. The model then claimed the context lacked the requested information.
Another program tried `paragraph["text"]`, inspected one paragraph's structure,
then collected matching indices without printing the selected material. It
answered with a place unrelated to the target paragraph. These are examples,
not a full causal classification of all failures.

The source evidence is question indices 0, 1 and 5 in the helper-allowed arm.
The audit preserves each exact generated program, returned observation and
native response. This analysis inspected code as text; it did not execute
saved generated programs.

The endpoint contract also matters. One helper-allowed response contained the
correct answer string `1964` but cited paragraph index 34, outside the supplied
paragraph range. It therefore failed the frozen output contract. We retain
that failure; it is not interchangeable with a wrong answer string.

## What changes next

Do not repeat this depth-permission comparison without a different learning
or information-access intervention. It cannot answer the depth question while
the policy never delegates. The queued structural-preview and procedural-SFT
experiments separately test basic input inspection and tool use.

Next, isolate communication from Python mistakes. Give two helpers different
halves of a new context and collect ordinary relevant-information reports.
Compare stopping there, asking each helper for more information generally,
and asking focused follow-up questions chosen by the parent. Keep the initial
reports and parent planning identical across those branches. Include a model
that reads the full source directly. If focused follow-ups help beyond merely
adding calls, there is a concrete behavior worth teaching the RLM.

This proposed comparison supplies the initial partition; it does not test
learned partitioning, and adaptive information gathering is not itself a new
idea. Its potential contribution is identifying when targeted communication
helps, then testing whether that decision can be learned and transferred.

## Limits and resume evidence

There are twelve shared question clusters, not 48 independent questions. They
were selected without inspecting model outcomes from the official development
data and were new to this local experiment; pretraining exposure is unknown.
The full contexts fit within the model's context capacity, so these questions
do not establish a need for long-context decomposition.

One episode hit an input-token refusal after three authenticated root calls.
Its final causal mapping was incomplete and remains unavailable under the
frozen analysis, not silently converted into an observed wrong answer.
The other 47 outcomes are scientifically available. The owner completed all
48 scheduled records, released the GPU, and took 417.84 seconds including
service ownership overhead. There were no optimizer updates.

Authoritative evidence:

- [Independent report](../../../../ARTIFACTS.md).
- [Exact audit, including code and response hashes](../../../../ARTIFACTS.md).
- [Follow-up proposal](../../../../ARTIFACTS.md).

The follow-up is CPU preparation, not a completed result. The original screen
and its scores remain unchanged.
