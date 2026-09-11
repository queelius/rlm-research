# MAIN-owned launch

Read READY.json and DESIGN.md. The sidecar owns no GPU allocation, service,
queue or port. MAIN binds the exact READY hash, command, allocation device and
deadline in the accepted parent. Verify is CPU-only and loads no model:

```
CUDA_VISIBLE_DEVICES= PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-partition-report-pilot-v1/run.py --verify
```

The accepted1800s parent supplies exactly one CUDA_VISIBLE_DEVICES device and
runs READY.launch_argv, a fresh direct child under this sidecar's outputs.
Set PYTHONDONTWRITEBYTECODE=1,OMP_NUM_THREADS=4,OPENBLAS_NUM_THREADS=1 and
TOKENIZERS_PARALLELISM=false. Use the pinned environment unchanged. Internal
1650s timer includes startup; parent owns final termination and release.

Checkpoint policy: requests before each call, calls after each complete or
interrupted call, episodes after each11-call coordinate, then OUTCOMES and STATUS.
Interrupted generation's output-token count is unknown, not zero. Shared
extraction calls appear once in physical cost and once in each hypothetical
structured pipeline. Summed call latency is not GPU wall time; STATUS records
elapsed time including cold startup separately. Source shard hashes are inherited
from authenticated WEIGHTS provenance and current size/mtime/inode checks;
preparation does not claim to have freshly rehashed8GB of weights.

No optimizer/checkpoint or training is produced. Preserve outputs on any failure;
the runner refuses existing output directories and does not resume or retry.
Before a new experiment or continuation, MAIN analyzes actual retained calls,
records what failed and freezes a new bounded decision. Do not edit this freeze.
