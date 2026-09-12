# Independent recursion-interface qualifier readout

Gate: **FAIL**. Failures: repeated_identical_action_loop.

| Mode | Correct | Wrong | Unavailable | Physical typed requests | Bad imports | Max consecutive identical actions |
|---|---:|---:|---:|---:|---:|---:|
| no_child | 0 | 5 | 1 | 70 | 0 | 18 |
| enabled | 4 | 2 | 0 | 31 | 0 | 2 |

Correctness uses each mode's fixed denominator of six. Missing, provider-failed, or unobservable episodes are unavailable, not wrong.

## Authentication

Semantic typed/role request-ID parity: `True`. Source/source-independent gate exact match: `True`. The two modes use byte-identical user prompts per task: `True`; the prompt contains the complete global-call/+decoder ABI: `True`.

Each mode report records prompt, task-hash, initial-prefix, system-advertisement, model-alias, usage, raw protocol, and semantic-audit counts. See `REPORT.json` for coordinate-level C/W/U rows and hashes.

## Posthoc old same-six comparison

- no_child: 0 correct, 4 wrong, 2 unavailable; 49 physical requests.
- enabled: 0 correct, 4 wrong, 2 unavailable; 109 physical requests.

This old subset was chosen after attempt002 and uses the same exposed tasks, contexts, weights, and seeds. It is useful only for diagnosing the explicit prompt intervention; it is not an independent baseline or generalization result.

## Decision

probe_repetition_mechanism: Replay only the affected task(s) with the exact trace prefix and compare deterministic next action with versus without the immediately preceding error observation.

A failed gate does not justify a higher request cap. The next comparison targets the identified import, repetition, observability, or audit mechanism.
