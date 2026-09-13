# Failed startup and explicit owned-process cleanup

The attempt002 owner stopped before scientific collection. Its inherited
`claim_service` rejected the new launcher's identity, and the same mismatch
prevented automatic release. The original terminal remains `released: false`;
it must not be rewritten to suggest automatic cleanup succeeded. All eight
scientific outcomes are unavailable, not incorrect.

MAIN verified the exact previously saved process identity in
`outputs/attempt-002/service/OWNED_PROCESSES/1166392-1106281859.json`, the recorded
command/config path, UID, process group and direct CUDA-child ancestry. Under
the coordinator flock, `terminate_owned.py` sent SIGTERM only to that owned
group. `OWNED_SIGTERM.json` records the identities and action. No files were
deleted and no unrelated process was signaled.

After the signal, the NVIDIA process query returned no compute processes and
`ps` found none of1166392,1166535,1166536. This was observed before00:24 UTC on
September13. The failed service's retained records explain the gap; GPU memory
and startup work must not be reported as completed scientific evaluation.

The selection-RL evaluator and independent normalization comparison take
priority over further work on this optional model port. Any later8B attempt
requires an additive lifecycle correction and new output directory.
