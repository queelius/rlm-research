---
schema: openai-mrcr-long-transfer-evaluation-design-v1
status: cpu-prepared-not-launched
claim_boundary: same-task length-transfer comparison, not neural context extension or broad generalization
---

# Paired base versus procedural-SFT checkpoint32 on frozen long MRCR inputs

Question: does the fixed 32-update procedural policy retain its short-input advantage on 16
outcome-blind, mutually exact-core-disjoint official MRCR contexts whose original external JSON is
16k–32k o200k tokens?

The base zero-LoRA transport and fixed checkpoint32 root use the same 16 coordinates, one fresh
seed per coordinate (`202609210000 + fixed_row_index`), temperature 0.5, top-p 1, top-k -1,
maximum 2,048 tokens per action, and six total root-plus-child turns. The child is the same fixed
released-base zero adapter in both arms. The neural root prompt remains below the 8,192-token
service limit; the much longer public context is mounted at `/context.json`. This does not extend
the neural context window.

Both arms run under the exact same qualified `terminal-strip-disabled` process-local condition.
It removes only the outer final-content strip and the successful ACP root-reply outer strip. It is
not a general lossless parser, does not repair gold answers, and does not change reasoning newline
handling or tool parsing. Raw exact is the primary endpoint; official MRCR `rfind` similarity and
normalized exact remain diagnostics without output cleanup.

The collector retains immutable input bytes, rendered initial token IDs, raw episode/code/tool
results, native provider IDs, prompt/action token IDs and native action log probabilities, causal
root/child mapping, actual usage, adapter binding, and unavailable outcomes. Gold stays host-only.
No checkpoint is selected from these outcomes and no optimizer runs.

Each arm has a 900-second science cap, 1,100-second owner cap, and 1,200-second external cap.
Failure or timeout in one arm must remain visible and must not suppress launching the other arm.

