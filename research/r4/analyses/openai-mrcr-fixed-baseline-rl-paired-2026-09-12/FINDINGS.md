---
schema: fixed-baseline-final-RL-findings-v1
source_readout_sha256: 4ac83a409099ca5af87d6f433e0872041e7ef5779c71378d5c1a21fff6473e85
status: exploratory_single_update_not_replicated
---

# One final-decision update: two short-panel gains, no long-panel gain

All planned episodes were available: short23→25/32 (two wins, no losses), long10→10/16 (no wins or losses). The two gains are in different short contexts, one repeat each; this is not32 or48 independent context units, nor a replicated training result.

| Short context / repeat | Exact before→after | Raw mechanism | Context's two repeats |
|---|---:|---|---|
| `omrcr-530d9996c900aa5d7b62` /0 | 0→1 | Two missing final ASCII spaces restored;932→934 characters,220→221 final-action tokens. Both finish with stop. | 1/2→2/2 |
| `omrcr-ef800b2a29008e4717f1` /1 | 0→1 | Substantial wrong content becomes exact,2591→2674 characters;675→714 final-action tokens. Official similarity.11668→1. Both finish with stop; not severe truncation or a length-cap failure. | 0/2→1/2 |

The second old answer does not exactly match any source-context message after marker removal. The verified finding is incorrect returned content after correct extraction, not a demonstrated retrieval of another source answer.

All48 first physical prompt/action token arrays match across cp32 and RL. All48 parsed Python programs and tool observations also match. Both gains followed the same exact clean-target stdout and the same final-decision prompt. No retrieval change is observed on these panels. This isolates where the observed output changed, not which parameter-gradient component caused it: weights differ, and no lossless-transport/clamp-only inference is justified.

There are four changed full token paths: the two gains above, one still-wrong short empty final, and one still-wrong long empty final. The short failure (`omrcr-746d5e1512abdfa38878`, repeat0) used the same two preceding root actions, then generated205→2048 tokens on its last action (stop→length), still returning an empty terminal. That adds1843 tokens. The long failure (`omrcr-long-508ab438696a81bec39f`) changed its last2048-token length-limited action but still returned empty; no cost or correctness change.

Thus short output cost rose1883 tokens:1 from the whitespace gain,39 from the content gain,1843 from a still-failing episode. Both short arms made66 calls with73557 prompt tokens; output23384→25267 (+8.05%). Both long arms made32 calls with34352 prompt and11431 completion tokens. No error, start-only, orphan or unknown-cost physical calls. Owner time: short402.00→404.95s; long252.20→247.68s. Training cost was43.74s science/56.20s owner, separately.

The update's negative-sample gradient was concentrated in whitespace (norm.003584), with EOS.0001254 and body4.33e-9. But the complete gradient is not equivalent to that component: total norm.004436, cosine(total, negative-whitespace).72824, and residual norm after removing negative-whitespace.003061. Positive-example reinforcement and EOS cannot be ignored; Adam normalization also prevents interpreting norm fraction as update fraction.

Next accepted action is paired decoding replication on all16 short contexts with two fresh seeds per context and both fixed models. This tests rollout sensitivity, not a new training seed or new dataset. No new training is justified merely by the two favorable outcomes.

After that replication and the fresh training-batch screen, the smallest targeted training-mechanism comparison is a saved-gradient ablation: keep the exact cp32 initial tensors, fresh Adam/LR and source batch, but remove only the already-saved negative-whitespace contribution before the one step. Compare against the existing full update, not another blind dose. Start with a fixed-state teacher-forced probe of the original first-action and final-decision prefixes: token likelihood by body/whitespace/EOS and actual distribution entropy at predeclared positions. This holds observations fixed and distinguishes a terminal-distribution change from shifts in the retrieval-policy distribution. It is a diagnostic component ablation, not an unbiased-RL-method or rollout-gain claim; do not execute or select a new checkpoint now.

Exact changed strings are retained locally in `CHANGED_FINAL_TEXTS.private.json` (0600), with public-friendly hashes, source paths and every changed turn in `CHANGED_OUTPUTS.json`. The analyzer never executed model-generated Python. Research-exposed contexts and unknown base pretraining remain limitations.
