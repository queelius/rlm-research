# Exact replay entrypoint

Run from any working directory; the destination must not already exist:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONPATH=/project/alex_phd/runs/rlm-research-r4/analyses/root-question-sensitive-sft-live-2026-09-10 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/analyses/root-qs-scale-harness-factorial-live-2026-09-10/reproduce.py --output-dir /tmp/scale64-replay
```

`reproduce.py` SHA-256 is
`1284cb6ef77a8f1bb5acac07847f1c429a1c367b654f9e74233108240b26fbbf`. Frozen manual annotations
SHA-256 is `71020e3499ef4e6447d3bd83067e26e90c9251fb6016a88d947387f596642157`.
The script authenticates the exact terminal relay, loads the pinned qualified native reader, rebuilds
all 64 native rows, reruns the physical/role cost union, extracts evidence, merges frozen manual
judgments, and refuses completion if core native or semantic values differ from the sealed artifacts.

Validation on 2026-09-10 produced 38 authenticated, 9 strict, 26 NULL, 12 faithful, and 7
faithful-plus-strict. The replay cost union produced 779 attempts (758 HTTP 200, 21 HTTP 400), known
usage 2,440,593 input / 148,713 output / 2,233,920 cached tokens, and 21 unknown values for each field.
