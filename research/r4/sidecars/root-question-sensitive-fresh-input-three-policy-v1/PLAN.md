# Fixed execution plan

MAIN may run `owner.py run` only after accepting the exact READY closure and after the current GPU
owner releases. The owner starts three services serially in fixed order: new-corpus SFT6, original
SFT6, fixed24. Each receives the same 72 frozen tasks, seeds, public files, fixed c32 child, native
limits, and four-worker collector. Each service has at most 1,650 seconds including startup and
release. The owner has 5,250 seconds of work, 5,370 seconds of ownership, and a 5,400-second outer
cap. All missing and failed endpoints remain in the 216-row inventory; there is no retry or refill.

Post-terminal analysis reports native/raw correctness and agent-reviewed faithful execution
separately, with authenticated malformed or empty finals as observed zero and missing or
unauthenticated results as NULL. The shared fixed24 policy is the paired comparator for both SFT6
models. No protected result selects a policy or changes the input set.
