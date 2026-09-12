---
schema: openai-mrcr-fourneedle-native-validation-report-v2
status: COMPLETE_NATIVE_VALIDATION
---

# Native-evidence supplement

The supplement authenticated 83 returned native calls and replayed 32/32 episode derivations exactly. Physical stop-token decoding matched the preserved root reply for 31/31 episodes with a physical stop; one checkpoint episode exhausted its 2,048-token action with an empty parsed reply and is retained separately rather than called a decode mismatch. All 32 episodes are scientifically available: True. Integrity issues: 0.

This does not independently reimplement the causal mapper or Qwen parser. It reuses the qualified collector's native validator, trace inspector, exact tokenizer renderer, and terminal-strip-disabled hook, then independently checks inventories, start/result equality, sampling, model aliases, provider IDs, prefixes through trace replay, and native terminal equality. It adds no model or GPU calls and does not replace the separate string/score audit.
