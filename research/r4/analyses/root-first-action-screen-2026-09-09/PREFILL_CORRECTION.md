# Correction: the model sampled the first tool-call opener

Additive correction, September 9, 2026. The original REPORT.md, SCREEN.json,
screen.py and raw experiment artifacts remain unchanged.

The sentence at REPORT.md:29, “The first-action tool prefix was already supplied
by the shared native setup,” is **incorrect**. SCREEN.json's “shared native
prefill” limitation repeats that misleading description. This was not a
historical-versus-BROAD change: the historical original and selected requests
also had no supplied `<tool_call>` continuation prefix.

## Actual historical evidence

I read all 48 first-request audit files referenced by SCREEN.json, authenticated
each against its existing source hash, and decoded the retained native/wire token
IDs with the pinned local tokenizer. No model or runtime was invoked.

- All 48 have identical native `tokens.prompt_ids` and physical
  `native_wire_request.body.token_ids`.
- All 48 end with only `<|im_start|>assistant\n` after the completed user message.
- All 48 sampled `completion_ids` begin with `<tool_call>`.
- Their wire sampling keys are exactly `logprobs`, `max_tokens`, `min_p`,
  `return_token_ids`, `seed`, `skip_special_tokens`, `stop_token_ids`,
  `temperature`, `top_k`, `top_p`. There is no grammar or tool-prefill setting.

Representative actual request IDs (not filename stems):

| Root | Actual request ID | Source file SHA256 |
| --- | --- | --- |
| Original `857a…` | `dee489e45a004df4921a1b770e7f3438` | `b3ed36e723589656de222600567e8ace33459ad7375b0b0a63964d35146d09f4` |
| Historical step8 `473210…` | `f4db2367fd6045bbaa0bd22c3d8e7707` | `196a634458c238193a909aea41c54b39251c5950157eb91bf78fc118539560f7` |

[PREFILL_CORRECTION_EVIDENCE.json](../../../../ARTIFACTS.md#unpublished-files "Not published: PREFILL_CORRECTION_EVIDENCE.json") retains all
48 exact paths/hashes, actual IDs, prompt tails, sampled completion heads and
sampling-key lists. SHA256:
`399ccc2fe00bae191a86d10f0b33e3220bc79c40458934a21742a54a5fb97fd3`.

## Why the source names were easy to misread

The pinned nano `_start` initializes system and user messages; `_call_model`
passes those messages and available tools, setting `parallel_tool_calls=False`
for ordinary calls. It does not append a tool-call opener. The executed Qwen3
renderer at lines 257–266 appends the assistant-role generation header and,
only when thinking is disabled, an empty thinking wrapper—not `<tool_call>`.
The historical `native_prefill_arm.py` names a native-renderer treatment whose
code enables thinking; that filename is not evidence of a literal tool prefill.

The prompt does supply a suggested procedure and worked code example. That is
instructional content, not a forced continuation prefix or grammar.
Decoded full first-request prompts confirm **48/48** contain both. The procedure
asks the root to inspect `context.txt`, select records relevant to the aggregate,
use direct Python for user-ID-only questions or recursive semantic classification
when needed, retain indices, check assignment coverage and avoid keyword guessing.
The worked example reads Instance text, takes `records[:4]`, supplies the six TREC
answer-type definitions, invokes `await rlm(...)` requesting a label array, prints
`child.answer`, and asks the root to continue covering the remaining records.
These are ordinary user-prompt bytes before the assistant generation header.

## Interpretation that survives the correction

The raw syntax screen itself inspected **sampled completion tokens**, so its
13/24 versus 22/24 usable JSON requests and paired final-answer tables are not
changed by this clarification. Malformed parsed messages still do not mean zero
generated tokens; an invalid or unfinished sampled JSON object can produce no
structured tool call.

The reported rationale must change: tool use was not forced by supplying its
opener. Nevertheless, both roots generated the opener in all 24 observations, so
this particular comparison shows improved valid serialization, **not an increase
in the observed decision to initiate a tool-call-shaped response**. Prompt
suggestion, voluntary generation, parser acceptance and actual Python execution
are separate facts. No causal mediation or broad planning conclusion follows.

## Additional source identities

- Original SCREEN.json: `ea1c8d222f99513661be029ddaa6e0e3a42d7ad6278b4f6e9a71c67cc7eb2e6f`.
- Original REPORT.md: `54d77d4ff70e806f3c121fef6c0f431bd9ff5a677ae4ed84dc134224ffb829dc`.
- Original screen.py: `7fd0980feca83c524cf38ff8c5b747184c390fd74e452899d98262d43d12ee81`.
- `/project/alex_phd/research-cache/2026-09-08-literature/leaf-contract.7HPUr5/nano__engine.py`:
  `2e04fe4589c75cef1ba3fdbbaead1275c40984588bf782e972c5556e3cc7f7ed`.
- `/project/alex_phd/research-cache/repos/prime-rl/deps/renderers/renderers/qwen3.py`:
  `75c4d4a96c7fe930b0fe80d83df894133e1319b364b033cf97fbea2d84e8e146`.
- Historical `sidecars/strict-rlm-client-qualification-v2/native_prefill_arm.py`:
  `40ed9b4c07dd097118e0aa5b2f27028160d1a915808afa5d675b6ce4e19f45e6`.

No pending uptake/adaptive outcomes were read for this correction. The BROAD
request cited by the parent motivated the check but was not needed as evidence
for these historical 48 statements.
