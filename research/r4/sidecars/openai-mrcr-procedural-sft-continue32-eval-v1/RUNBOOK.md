# Runbook

MAIN first runs the `checkpoint_seal_argv` after the continuation trainer has a clean terminal and
committed checkpoint-0032. It then runs `train32`. Only if that raw train result passes the immutable
8-exact/4-context/all32-available gate are the fixed `held-base` and `held-checkpoint32` stages run,
in that order. Each stage has owner cap900 seconds and external cap1000 seconds. No retries,
intermediate-checkpoint selection, or held-query substitution are allowed.

