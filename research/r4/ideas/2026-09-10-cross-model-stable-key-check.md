---
id: cross-model-stable-key-check
status: prepared
date: 2026-09-10
---

# Does stable-key support survive a model-size change?

The 4B model strongly benefited when each output carried a stable positional key. The smallest model-generalization check reuses the exact exposed 16-context panel on released Qwen3-8B, comparing labels-only, sequential numeric keys, and opaque stable keys. This changes model weights and tokenizer together, so it tests portability to another released model in the same family—not a clean causal effect of parameter count.

Run 144 new calls in one A100-40GB allocation (2400-second cap); reuse, rather than rerun, the 4B results. Promote only to a fresh-context 8B replication if both keyed forms improve the paired context estimate without reducing availability and at least 12/16 contexts improve.
