---
question_id: controller_training
status: complete_exploratory_interface_control
date: 2026-09-12
result_sha256: 96ad0cf575be1e04b54b9afc3358b14cf497060bcf81dcd9bca60f361dc3fb2e
unique_contexts: 8
paired_seeds_per_context: 2
scheduled_episodes: 32
available_episodes: 32
optimizer_steps: 0
publication_readiness: local_mechanism_not_task_improvement
---

# Explaining the input structure fixed Python errors, not retrieval

The model had to find a particular assistant reply in a saved conversation.
We compared its original instructions with a short, automatically generated
description of the input's structure: a list of message objects, their field
names and types, and the number of user and assistant messages. The preview
contained no message text, answer, target position or retrieval procedure.

The same eight conversations were tested twice per condition with paired seeds.
All 32 results were available. No training occurred.

| Measurement | Original instructions | With structural preview |
|---|---:|---:|
| Exact answers | 1/16 | 0/16 |
| Python traceback observations | 18 | 0 |
| Root model calls | 47 | 32 |
| Returned observation characters | 116,448 | 40,732 |
| Episodes with an observation of at least 18,000 characters | 4 | 0 |

The preview clearly changed how these attempts used the input, but did not
produce a task-level improvement. Its exact-answer comparison had zero wins
and one loss. Raw official text-similarity scores averaged 0.265 without the
preview and 0.077 with it. These are eight context clusters, not sixteen
independent contexts or a statistical confirmation.

## The remaining mistake is easy to explain

The model often selected a request rather than the reply to that request.
Here is a simplified illustration of an observed failure:

```text
User: Write a social media post about physics.
Assistant: Here is a post about gravity ...
```

Asked to retrieve the post, the model searched messages whose role was `user`
and returned “Write a social media post about physics.” It now knew how to
read the list, but selected the wrong kind of message.

In a static inspection of all sixteen preview-condition first programs, three
explicitly searched only user messages, one explicitly searched only assistant
messages, and twelve searched both roles or discarded role information. None
implemented the intended user-request-to-following-assistant-reply procedure.
These are descriptions of the saved first programs, not evidence that every
possible selection strategy must use that exact procedure. Saved code was
inspected as text and was not executed.

The sole exact answer without a preview followed two Python tracebacks and
a truncated, 20,000-character observation. It should not be described as
correct first-pass programmatic retrieval. Removing broad observations can
also remove opportunities for the root to recover by rereading the input;
that is a plausible explanation to investigate, not a proven causal account.

## Decision

Do not promote the preview alone as improved task solving, and do not run
another identical screen. Retain it as a useful input-access control. The next
training comparison should teach how to identify the requested message, not
merely how to access fields. The already queued procedural-SFT run tests that
behavior; its outcome is not inferred from these interface results.

Automatic structural metadata is already familiar in RLM-style systems.
The research value here is separating input-access errors from retrieval
errors, not claiming a new architecture for printing field names.

## Evidence and limits

The [reproducer](derive.py) rechecks the frozen source closure, all episode
hashes, all condition-specific initial prefixes, the shared causal mapping
against 79 native returns, all saved derived fields, and the raw-string scorer.
Its [machine-readable result](FINDINGS.json) contains hashes and per-episode
metrics without reproducing conversation text. This reuses the original
mapper and scorer; it is not an independently implemented raw-wire audit.

The automatic first-program detector flagged ten top-level schema mistakes
without the preview and none with it. That detector is heuristic and can
misread guarded code or variable reassignment. Absence of its flag does not
mean the program performed correct retrieval. Missing Python actions remain
separate, never classified as successful access.

Character counts are not byte counts. The independently recomputed UTF-8
observation totals are 117,233 and 41,080 bytes respectively. These measure
returned observations, not everything Python read. Neither condition made a
child call. The owned workflow took 410.57 seconds and released the GPU.
The contexts were already research-exposed training-side examples; no held-out
generalization or absence from pretraining is established.
