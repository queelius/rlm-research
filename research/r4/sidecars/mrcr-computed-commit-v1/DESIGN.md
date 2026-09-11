# Approved computed-string commitment experiment

Parent accepted the 2026-09-09 core-harness audit recommendation under the user's
autonomous experimental authority. This implements that narrow decision only.

Six previously inspected MRCR development documents/questions; original immutable
Qwen3-4B adapter; native Qwen3Renderer(enable_thinking=True), T0, full support,
2048 sampled tokens/call. Complete context is read-only /context.txt. Gold stays
host-only. No sketch, new leaf strategy, weight change, retry or answer repair.

A root computation may use at most five completed model calls, then explicitly call
submit_text(value), with exactly one plain str in a successful Python cell. UTF-8
ceiling is maximum selected context byte size + 1024, chosen before reading gold.
Empty strings remain observable candidates; invalid types, duplicate calls,
invalid UTF-8 and oversize attempts are recorded, never coerced. Cell exceptions
invalidate even an earlier successful call. No stdout parsing or variable guessing.

The accepted bytes are one terminal branch. The same actual conversation/candidate
then receives exactly one native restatement call, up to six calls total. This
call's tools are recorded but never executed, and no retry follows truncation,
tool requests or infrastructure errors. The restatement observation contains the
exact candidate string and a fixed instruction; its full request is retained.
Candidate is persisted before the extra call, so restatement failure cannot erase
the direct branch. An ordinary earlier textual terminal is non-submission, not a
candidate fallback. Both official raw scores and strict terminal validity are
reported separately; a faithfully committed wrong value stays wrong.

One sequential owned container per document; 200 seconds/episode and 1200 seconds
global model/runtime budget (cleanup may add grace). Exact native token IDs,
sampled logprobs and logical prompt/completion usage are retained. Cache usage is
raw-provider-derived when present, otherwise unknown. No entropy/calibration claim.

An additive container-only overlay replaces the pinned REPL result handling and
adds a structured Jupyter user-expression MIME envelope. Successful cell status,
submission attempt state and text are separate from display. It changes no shared
clone or image tag. The core's existing FINAL_TEXT behavior is the reference;
core ABI is unchanged. This is a developmental finalization/serialization test,
not six independent confirmations or a learned-planning result.

The parent-approved common task-system suffix explicitly overrides nano's generic
"stop calling tools and state your final answer" instruction for the top-level
computation. Ordinary child returns and the one requested final restatement remain
legal. The original tasks and reconstructed pre-amendment source are retained;
questions, contexts, seeds and byte cap do not change. Final native-wire CPU proof
checks that the suffix is actually in the shared system prompt.

The legal commitment cap is not a promise that a restatement fits a model call.
Record exact already-rendered final prompt length, advertised context cap and
requested 2048-action limit. Separately record canonical tokenization of the
candidate as a budget diagnostic, never substitute it for sampled physical IDs.
Input overflow, canonical copy/output-window exposure and length-stopped finals
are separate from semantic copying differences. Canonical tokenization is not a
proof of the shortest possible encoding; reasoning and stop tokens also consume
capacity. No call is retried or repaired, and original raw scores stay intact.

Inherited nano transport retries are removed only in this owned overlay, with
max_retries=0 at both SDK hops. The paired native path retains Qwen rendering,
sampling and sampled logprob semantics. See RETRY_NOTE.md for the live campaign's
unchanged inherited retry capability; no observed campaign retry is inferred.

This is filesystem-isolated, not network-isolated. Submission state is trusted
experimental instrumentation inside the model's own REPL, not an adversarially
tamper-proof capability. Gold, host home and research files are not mounted.
