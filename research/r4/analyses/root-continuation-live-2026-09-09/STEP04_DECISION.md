# Step-four milestone — 2026-09-09 01:51:34 UTC

The continuation made one genuine additional optimizer update: inherited Adam3 → new Adam4 across all 504 actual optimizer states. Saved adapter, Adam, RNG and state hashes match the exact predecessor and new COMMIT; parameter order and optimizer options are unchanged. The loaded step3 adapter audit confirms exact tensor values/dtypes. This establishes execution fidelity, not improved task performance.

The real step-four group contains 19 episodes from five mixed-reward tasks: 4 + 3 + 4 + 4 + 4. The original 29 admitted episodes remain 12 correct and 17 wrong, with three training exclusions. Endpoint accounting instead has 12 correct, 18 wrong and two unobservable. The recovered overflow episode is still training-null. Its task (`root-credit:03:0`) contains two admitted correct episodes and no admitted wrong episode, so it remains excluded from the mixed training group. This is a concrete illustration of the declared policy-induced failure-censoring limitation, not a reason to change admission post hoc.

Training used 44 root turns and 15,343 root action tokens, with zero child or observation credit. Gradient norm0.11119576, adapter delta L2 0.10248164; distribution guards passed. Optimization took35.610s and update plus checkpoint36.753s. Dispatch to INPUTS took31.143s (imports, authentication and loading combined; not pure model-load time), while dispatch to RESULT took67.909s. New service startup took42.283s. The reused round04 collection's361.261s are historical, not continuation rollout time.

Decision: preserve the frozen continuation and await validation four. No prompt, admission, optimizer, selection or budget change follows from this execution milestone.

Evidence: `step04-20260909T015134.613049Z.json` SHA256 `62d2a6af8133300662c8a9313baf778cf97150cfe903008273f880be69550850`; actual Adam audit cached in `STEP_04.json`. Observer CPU process time3.49s, GPU calls0.
