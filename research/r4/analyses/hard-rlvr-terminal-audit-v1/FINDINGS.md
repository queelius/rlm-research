# Hard-RLVR terminal audit

## Result

The original attempt correctly refused to train under its declared rules, but its single
`runtime_valid` flag hid useful distinctions. This read-only audit recomputed all 120 episode
records against the frozen tasks and the exact sealed `verify_terminal` implementation.

| Category | Count | Meaning |
| --- | ---: | --- |
| Planned episodes | 120 | Five rungs of 24 episodes |
| Execution exceptions | 102 | No terminal output was retained, so terminal validity and correctness are unobservable |
| Execution completed | 18 | A terminal output and controller trace were retained |
| Structurally trainable trace | 18 | Every captured turn passed the trainer's token, label, mask, and log-probability invariants |
| Predeclared `runtime_valid` | 0 | No episode had exactly two controller turns and exactly one leaf call |
| Terminal schema valid | 2 | Exact `{"kind":"count","value":integer}` output |
| Terminal correct | 0 | No retained terminal output matched its gold answer |
| Malformed JSON | 9 | Observable output, but not JSON |
| Wrong JSON schema | 7 | Observable JSON, but not the required object |

The two schema-valid but wrong episodes were:

- `05e1ac29...` in rung 2 returned `0` instead of `5`; it used four controller turns and no
  leaf call.
- `21cd9595...` in rung 5 returned `0` instead of `12`; it used three controller turns and no
  leaf call.

The other 16 retained outputs were terminally incorrect because they were malformed or used the
wrong schema. Their exact split was nine malformed JSON and seven wrong-schema JSON. For the 102
exception rows, correctness is not set to false: the episode records discarded any partial
output, so terminal parsing is unobservable.

## Exception audit

All 102 exceptions were `EpisodeModelFailure`:

- 87: `controller did not submit a final response within 4 turns`
- 14: `upstream request exceeded the absolute timeout`
- 1: `subcall limit would be exceeded: requested 1, used 1, limit 1`

`exceptions.jsonl` records the exact type and message, a type/message signature hash, traceback
hash, task identity, and source episode hash for every exception.

## Methodological confound

The original admission rule required exactly two controller turns and exactly one leaf call.
Among the 18 completed episodes, the observed shapes were:

- four with two turns and zero leaf calls;
- eight with three turns and zero leaf calls;
- two with three turns and one leaf call; and
- four with four turns and zero leaf calls.

Thus the gate selected a particular decomposition shape, not merely a usable trajectory. It
simultaneously determined whether the answer would be verified and whether the trace could train
the policy. This confounds behavioral compliance with technical trainability: all 18 completed
traces satisfy the actual token-level training invariants, yet all were discarded before terminal
reward. It also makes task difficulty impossible to estimate from the declared valid set because
that set is empty.

This audit does **not** establish that updating on all 18 traces would improve the model. All 18
observable terminal answers were wrong, and the 102 exceptions supply no observable terminal
outcome. The defensible conclusion is narrower: the attempt failed primarily at controller
execution and output discipline, and the shape gate discarded potential negative-reward training
examples for a reason unrelated to whether their controller actions were trainable.

## Proposed v2 record and policy

`proposed_v2_schema.json` makes five dimensions orthogonal:

1. `execution_completed`: whether a terminal output survived.
2. `trace_trainable`: whether captured controller tokens satisfy the optimizer's invariants.
3. `terminal_schema_valid`: whether the observable output has the required schema.
4. `terminal_correct`: whether the observable output is correct; null only when output is
   unobservable.
5. Decomposition measurements: controller turns, leaf calls, and whether a reference shape was
   matched.

For v2, an episode is update-eligible when execution completed, the trace is structurally
trainable, and the terminal is observable. Exact terminal reward is 1 for correct output and 0
for every observable incorrect output, including malformed or wrong-schema answers. Exceptions
remain excluded because their terminal answer is unobservable. Turn and leaf counts remain
descriptive measurements or can receive a separately declared auxiliary reward; they do not
silently control update eligibility.

## Files

- `episode_audit.jsonl`: all 120 recomputed row classifications and source hashes.
- `exceptions.jsonl`: separate exact-error audit for the 102 exception rows.
- `summary.json`: totals, rung breakdowns, shape counts, errors, and input provenance.
- `PROVENANCE.json`: immutable source identity and audit method.
- `MANIFEST.json`: SHA-256 seal over all authored and generated audit files.
