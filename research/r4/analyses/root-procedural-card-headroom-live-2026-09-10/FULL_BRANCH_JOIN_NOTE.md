# Additive post-outcome full-branch accounting note

The prelaunch final reader and its output are unchanged: all34 available finals had unique exact-body/full-token/logprob joins. During the later all-branch audit, repeated c32 calls with identical request body/seed returned identical completion token/logprob vectors. The body/token-only matcher correctly rejected multiple candidate occurrences. This was not a scientific final NULL or score defect.

For the additive occurrence ledger only, `evidence.py` requires a unique equality between the typed **response.id** and the raw **response.request_id** (both provider-ID namespace), followed by unchanged exact body and full completion token/logprob equality. Typed request UUID remains separate. Thus repeated physical calls remain separate, not merged or selected by content. Missing/conflicting identity remains an error. No sampled code is executed and no unrecorded endpoint final is promoted.

The first post-outcome evidence assembly also hit a local `diff`/`diffs` variable-name typo before writing its artifact; corrected without altering any frozen reader, source, raw output, primary score or availability. Synthetic repeated-occurrence and independent mathematical oracle tests accompany the additive closure.
