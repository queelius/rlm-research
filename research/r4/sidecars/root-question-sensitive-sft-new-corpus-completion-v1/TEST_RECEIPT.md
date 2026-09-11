---
created_utc: 2026-09-11T00:04:00Z
status: passed
---

# CPU qualification receipt

- `python -m pytest -q test_recovery.py`: **5 passed in 8.32s**.
- `python owner.py verify`: identity
  `80c6477d0873d1225adad9df7f80be8600d83a999e80373e906dd3deae62bc49`.
- The actual training interpreter imported the unchanged `rep_train.py` successfully.
- The actual native interpreter parsed `collect.py --help` successfully and exposed the exact
  `capture/free`, plan, binding, endpoint, output, stop, and deadline contract.
- With a non-secret fixture credential, the actual native interpreter loaded the complete owner
  dependency chain and exposed callable start, command, and release operations. The generic system
  Python lacks `verifiers`, as expected, and is not an authorized production owner interpreter.
- The retained source failure test checks both the missing-CUDA exception and the original command
  receipt's `gpu_visible_to_command=false`. The recovery launcher test observes the assigned CUDA
  device in the real subprocess environment and the owned-process stop path.

The checkpoint-dependent binding cannot resolve before training by design; `selected()` requires
the complete checkpoint-6 `RESULT.json`, six-state ancestry, and file hashes. The owner invokes it
immediately after training and before starting the readout service.
