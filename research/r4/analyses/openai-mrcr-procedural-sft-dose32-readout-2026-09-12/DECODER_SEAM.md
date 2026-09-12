# cp32 train readout: retrieval acquired, final-content fidelity is mixed

The frozen scored result remains **24/32 raw exact, 32/32 available**. All 32 first programs match the authored teacher AST and all 32 produce a clean correct target observation; there are no observed wrong selectors, schema errors, or broad dumps. This is strong procedure-acquisition evidence on the fixed training panel, not a held-transfer claim.

Of the eight scored failures, seven differ from gold by deletion of precisely two final ASCII spaces. Action-token inspection separates three parser-only losses from four other whitespace failures. The eighth changes two curly apostrophes. Therefore neither “all eight are parser bugs” nor “the remaining failures need more retrieval training” is supported.

## Exact failure attribution

| Record / task | Gold → semantic action-token text | Semantic text → saved parsed/root final |
|---|---|---|
| `omrcr-b6df230e787db5b5dc70`, Beatles riddle | Exact | Deletes final two spaces |
| `omrcr-761b3b3a695b4f901881`, spirits riddle | Exact | Deletes final two spaces |
| `omrcr-5b0597c34821c3e04a08`, scissors poem | Exact | Deletes final two spaces |
| `omrcr-99027bdfd94d88916c23`, capacity letter | Model omits final two spaces | No further change |
| `omrcr-08d6010dc261b9832b1d`, society poem | Model omits final two spaces | No further change |
| `omrcr-2890a9f3655bea998dee`, religions poem | Model omits final two spaces | No further change |
| `omrcr-9f431a2f2bea9f0c243c`, departments riddle | Model adds two newlines after intact gold | Deletes gold's two spaces plus the extra newlines |
| `omrcr-9be48f691b9f7cea8f6c`, freedom play | Model replaces U+2019 with ASCII apostrophe at offsets 1358 and 1376 | No further change |

Thus 3/7 whitespace failures are exact before parsing; 3/7 already omit spaces and 1/7 already adds newlines. Departments remains incorrect under honest whitespace preservation. No trimming, Unicode repair, or marker repair is an authorized reward change.

## What was actually decoded

[decoder_audit.py](decoder_audit.py) replays the installed `Qwen3Renderer.parse_response` on all 32 saved final action-token arrays. It reproduces all 32 native parsed finals exactly, and each saved native final equals its scored `trace.root_reply`. Each completion has exactly one configured stop token, at its final position. The exact production `_strip_stop_tokens` truncation removes that terminal protocol token; `tokenizer.decode(..., skip_special_tokens=False)` then preserves all content bytes. None of these 32 spans contains reasoning, tool, or other special-token framing. No reasoning span, tool payload, or raw protocol delimiter is being credited as final-answer content.

On these bare-content spans, **27/32 match gold before parsing**. This is an inert action-token diagnostic only, not a new rollout score or retroactive replacement for 24/32. Three exact answers end in the two-space token 256 before stop token 151645. The audit compares exact UTF-8 text hashes and canonical action-token-array hashes, validates the native recorder's own token hash, and records every non-equal diff operator with zero-based Unicode code-point offsets. Generated Python was never executed; no model calls or GPU were used.

## Confirmed call chain and two real clamps

1. `renderers/client.py:370` calls `renderer.parse_response(completion_ids, tools=tools)`; line 399 exports `parsed.content`.
2. `renderers/qwen3.py:290` delegates to `parse_qwen3` with the configured stop, tool, and reasoning boundary tokens.
3. `renderers/parsing.py:141` truncates at the first stop; line 154 decodes without skipping special tokens. `parse_qwen3` preserves existing tool/reasoning extraction. Its line 289 applies **`content=text.strip()`**: the first confirmed clamp.
4. `verifiers/v1/clients/train.py:143` builds the typed assistant message from `result.get("content") or None`, without stripping nonempty content. The frozen native records contain this parsed value.
5. Host `verifiers/v1/acp/__init__.py:154` validates the received typed turn; **line 289 assigns `trace.root_reply = turn.reply.strip()`**: the second confirmed clamp. Its returned `ProgramResult.stdout` retains `turn.reply` unchanged. `rlm/harness.py:163` consumes snapshot metadata and does not restore the exact reply.
6. The inherited procedural collector's `collect.py:217` reads `trace.root_reply`; the continue32 collector delegates to this implementation. This is the value compared to gold, not an untrimmed alternate output.

The addendum includes two actual `ACPHarnessSession._run` CPU invocations with fake transport packets: one with two final spaces, and one containing leading spaces, a newline, a curly apostrophe, final spaces, and two final newlines. In both, actual `ProgramResult.stdout` preserves the supplied text and `trace.root_reply` equals its stripped form. This proves the host boundary behavior; it is explicitly **not** a complete native-agent transport roundtrip. Existing saved parsed/root equality does not establish the fidelity of every intermediate transport layer for a newly untrimmed response. A new full-path fake-final fixture is required before the ablation is admitted.

`parsing.py:286` also applies `after.strip("\n")` in the reasoning branch. A final-`.strip()`-only intervention leaves that behavior intact and must not be advertised as a general lossless reasoning parser. The `qwen3.py:96/104` strips are in `_query_boundary_text`, used to classify user/tool-response boundaries; they are not evidence of response-content mutation and are out of scope. Other `last_reply` helpers and historical assistant rendering are also out of scope unless an actual exercised path demonstrates their involvement.

## Smallest informative next comparison

Prepare an experiment-local **terminal-strip ablation**, scoped to the active Qwen3 parser and ACP scored-root storage. Preserve stop truncation, reasoning/tool parsing, tool-call validation, marker text, and all ordinary final-content whitespace. Replace only the terminal content clamp and store the verified raw `ACPTurn.reply` at the scored root boundary, using process-local hooks (for example the already-called successful `acp_turn_result` callback for root storage). Do not mutate shared dependencies, running owners, the original scorer, historical prompt rendering, or gold. Label the condition narrowly because the inherited reasoning newline rule remains.

Use focused regression fixtures covering spaces, leading/trailing newlines, curly apostrophes, unchanged tool/reasoning boundaries, malformed tool handling, and the actual native final → typed response → ACP root → collector path. A genuine added newline must remain a raw-exact failure; curly-to-ASCII replacement must remain a failure.

Then at most one new 32-episode arm: authentic fixed cp32 on the same fixed train32 contexts and original seeds, identical root/zero-child binding, prompt/prefix construction, temperature 0.5, decoding budget, engine configuration, and scorer. The existing old-parser arm can be reused only after exact binding/seed/physical-prefix equivalence is verified. Compare token identity as well as parsed/root fidelity; matching seeds alone does not establish identical generated completions. Retain the old 24/32 arm and every new episode, with unknowns explicit. Do not retrain SFT, select another checkpoint, or infer held regression from an unpaired baseline. Fixing this reward-facing seam takes priority over choosing a terminal-copy RL objective, but it does not erase the five genuine model text differences.

## Evidence and reproducibility

[DECODER_SEAM.json](DECODER_SEAM.json) contains all 32 per-row action-token, semantic-content, native-parsed, scored-root, gold, episode, and native-file hashes; exact diff operators; 114 source-file hashes; protocol-scope assertions; and the actual ACP CPU proofs. Text hashes are SHA256 of exact UTF-8 bytes, not stripped or JSON-escaped strings. The reference readout report SHA is `2c4f6d1d36b63b0c8520c6fc062ea0a6b7280653e66d47516c10563fd194fa55`. Source renderer, train client, ACP boundary, harness, collectors, tokenizer files, and this audit script are hashed independently. The original analyzer receipt and scored run files are untouched.

Reproduce without GPU or generated-program execution:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/analyses/openai-mrcr-procedural-sft-dose32-readout-2026-09-12/decoder_audit.py
```
