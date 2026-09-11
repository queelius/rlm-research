# Reproduce and verify

This audit reads but never writes the source attempt. The driver refuses any source-hash drift.

```bash
root=/project/alex_phd/runs/rlm-research-r4/analyses/hard-rlvr-terminal-audit-v1
python=/project/alex_phd/envs/prime-rl-5990b1b/bin/python

"$python" "$root/src/terminal_audit.py" --check-only
"$python" -m pytest -q "$root/tests/test_terminal_audit.py"
/project/alex_phd/envs/prime-rl-5990b1b/bin/ruff check "$root/src" "$root/tests" "$root/scripts"
/project/alex_phd/envs/prime-rl-5990b1b/bin/ruff format --check "$root/src" "$root/tests" "$root/scripts"
"$python" "$root/scripts/seal_manifest.py" --verify
```

To deterministically regenerate `episode_audit.jsonl`, `exceptions.jsonl`, and `summary.json`, run
the driver without `--check-only`, then reseal the manifest.
