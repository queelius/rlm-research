# Fixed held16 readout for both token-TIS doses

This conditional evaluator reuses the exact 16 held contexts, prompts, one-rollout seeds
`202609132100..202609132115`, raw official scorer, root/child turn cap, temperature 0.5, and
2048-token action cap prepared for the shaped-root endpoint. Those coordinates have not been
queried by that failed endpoint, but they have been exposed separately to the procedural-SFT
study; this is an exploratory dose readout, not independent confirmation.

The three predeclared arms are released base weights, token-TIS LR1e-5 step1, and token-TIS
LR1e-4 step1. Both updated branches must exist, authenticate as independent step1 commits from
the same initial trainable identity and saved gradient, and pass the fixed 10x dose relation.
The base and fixed child use the same exact-zero rank8 transport adapter. Each arm owns and
releases a fresh service. No checkpoint or dose is selected from evaluation outcomes.

Primary output is paired raw exact. Raw official similarity, >=0.90 frequency, shaped reward,
availability, root/child calls, token use, and deadline censoring remain separate diagnostics.
No output trimming or newline repair is applied.
