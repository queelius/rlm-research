# Fixed procedural-SFT dose: checkpoint4 versus checkpoint32

Some train episodes executed the exact authored teacher AST with raw-exact final and no Python error/dump; quantify extent separately from held transfer

| Stage | Raw exact / available / planned | First teacher AST | Schema-error episodes | Dump episodes |
| --- | ---: | ---: | ---: | ---: |
| train_checkpoint4 (TERMINAL_SNAPSHOT) | 0 / 28 / 32 | 0 | 31 | 17 |
| train_checkpoint32 (TERMINAL_SNAPSHOT) | 24 / 32 / 32 | 32 | 0 | 0 |
| held_base (TERMINAL_SNAPSHOT) | 2 / 29 / 32 | 0 | 17 | 12 |
| held_checkpoint32 (TERMINAL_SNAPSHOT) | 17 / 32 / 32 | 0 | 0 | 0 |

Matched train dose comparison: 28 available pairs; checkpoint32 wins/losses 21/0; 0/32 first actions unchanged.
Fixed held gate open: True. Genuine held base/checkpoint32: 29 available pairs, wins/losses 15/0. Missing held results are not transfer failures.

## Teacher-forced fit versus execution

Checkpoint32 clean correct target observations: 32; correct print followed by an available nonempty wrong final: 8; clean wrong-record prints: 0. These distinguish selector evidence from the final-copy boundary; broad dumps do not count as clean retrieval prints.
- checkpoint4: COMPLETED_FOUR_UPDATES; pre-update action CE 1.422542 → 1.098519.
- checkpoint32: COMPLETED_32_TOTAL_UPDATES; pre-update action CE 0.966467 → 0.000385.

Lower teacher loss alone is not procedure acquisition. Inspect exact teacher-AST clean successes separately from other role/ordinal candidates and broad dump/copy outcomes. Train fit is teacher-exposed; any transfer statement must use the actual final32 held pair. No unmatched baseline supports a regression claim.

Integrity findings: 0. Full evidence and fixed source hashes are in REPORT.json.

- Generated code is parsed as text/AST only; no exec/eval, model call or GPU.
- Exact teacher AST plus saved clean execution and raw exact is narrower evidence than arbitrary program correctness; pattern flags need review.
- Train checkpoint4/32 comparisons require identical coordinates, seeds and physical initial token prefixes. No unmatched base regression claim.
- Held comparison is only genuine fixed final32 versus its matched base,16 contexts x2 repeats; not32 independent contexts.
- Availability uses the previously checked observer taxonomy conditional on collector causal mapping; raw finals and initial prefixes independently checked.
- Checkpoint32 full adapter/Adam/RNG qualification is reused from the evaluator receipt, not rehashed or replayed here.
- Teacher loss and collected gradient metrics are not independent backprop verification. No checkpoint selection or feedback into training.
