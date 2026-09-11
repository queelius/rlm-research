# Interruption is not an implemented automatic resume path

The launch and training CLIs are fresh-only and require a new exact attempt.
This READY does not promise executable resume, new-node launch or automatic recovery.
MAIN should start only if the full3600s envelope fits before19:07:17 UTC.

All completed captures and completed arms remain immutable. A future separately
reviewed continuation can reuse a complete CORPUS_READY after authenticating every
member and original prepared identity. A partial16-example capture is not a usable
corpus under this design and must not silently omit/retry examples.

Each complete optimizer update saves adapter/config, Adam, Python/Torch/CUDA RNG,
full-pass cursor, corpus identity and previous-state chain. An interrupted update
has no committed optimizer step; only the last complete checkpoint could be used
by an explicit later continuation. Do not restart fresh Adam and call it resume.
Completed training arms must not be retrained or replace their fixedfinal selection.

After renewal, rediscover actual node/environment/runtime availability, user/UID,
GPU identities, MIG assignment and owned-service processes; inherited paths and
the ephemeral local runtime store may no longer exist. No fallback or CPU/GPU
device substitution is authorized by this document. Preserve elapsed budget and
original failure artifacts in any future separately accepted continuation.
