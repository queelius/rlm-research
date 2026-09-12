# Independent MuSiQue task-directed follow-up readout

This CPU-only analyzer is pinned to accepted `outputs/attempt-003`. It reads no partial result: run
`run_if_terminal.py` after `OWNER_TERMINAL.json` exists. Before that point it prints one `PENDING`
record and exits without polling or writing an outcome.

```text
CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/python run_if_terminal.py
```

The analyzer independently decodes raw native completion token IDs, authenticates request bodies,
seeds, model identity, finish reasons, usage and saved prompt hashes, and reconstructs strict answer
EM/F1 and support EM/F1. It preserves unknown endpoints and costs. It checks the shared report and
planner parent across stop, broad and targeted; broad versus targeted is the equal-call targeting
contrast. Lexical host-answer presence in additional reports is descriptive mechanism evidence only.
No generated code, host-gold model prompt, model query or GPU work occurs.
