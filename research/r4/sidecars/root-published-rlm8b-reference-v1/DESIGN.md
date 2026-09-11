# Published RLM8B intended-interface reference48

CPU implementation approved by MAIN; GPU launch remains a separate MAIN decision. This implements the approved [design](../../ideas/2026-09-10-published-rlm8b-intended-scaffold.md), not a new training recipe.

Question: under a paper-derived intended RLM interface, can the released RLM8B package acquire semantic evidence, compute the requested operator, and finish on nonzero tasks, compared with its Qwen3-8B base in the same scaffold? Root and plain-LM child weights change together. This does not separate model size, posttraining, scaffold, or root-only effects from earlier4B studies.

## Fixed comparison and source exposure

Base first, then RLM8B; 24 paired tasks each, all QSR readout04–11 contexts, count-union/distinct-all/weight-single, one paired seed. The panel has192 unique public records,23 nonzero targets and1 zero per policy. Contexts have prior root-research and child-training exposure. No task/outcome/quality selection; neither a fresh holdout nor a claim of broad generalization. Eight context clusters, not48 independent samples. Public records retain their exact JSONL text and id/user/text/weight fields. Host labels/answers remain outside worker packages. Child observations may be wrong; none are repaired or filtered.

Master2026091001 and task seeds2026091101–124 replace the colliding proposed981651xxx namespace. The per-call seed hashes task seed/role/logical index, paired across policies. Prepared-source inventory receipt is frozen. Same root and child sampling: temperature.6,top_p.95,top_k20,min_p0,no repetition/presence/frequency penalty. Each initial prompt is tokenized with both actual local tokenizers and the common released RLM template; raw per-call tokens are checked against actual service returns. No reasoning parser, tool parser, grammar, SDK retry, forced acquisition or answer fallback.

## Historical/paper boundary

Official MIT clone commitbeb0603f1efa4725a7bb4ae73a1a870e140fe7d5 is a compatible historical candidate, NOT an authenticated training commit. We retain its environment, prompt metadata/user continuation, Python execution, and FINAL/FINAL_VAR parsing. The wrapper changes only transport/trace ownership, bounded stopping and isolation; it does not use our ACP root prompt.

The system prompt is mechanically reconstructed from arXiv2512.24601v2 AppendixC TeX plus its Qwen8B diff. MAIN approved contextual insertion of standalone FINAL_VAR after the closed example because printed hunk line numbers are misaligned. Raw TeX, published diff, reconstruction7198621f…, applied diff and receipt are preserved. Published ~24k-character versus32k-token inconsistency, unescaped Gatsby quote, and chunk/comment mismatch remain. It is paper-derived intended-interface reconstruction, not verified training bytes. The one brace-rendering pass is frozen separately; the historical builder receives escaped rendered braces and preserves the resulting exact system text. Its additional metadata and first-action safeguard are also captured.

## Execution and measurement

One8B full-weight BF16 service at a time, no LoRA/quantization/YaRN. Common RLM chat template;32768 context,max2sequences,4096batched tokens,.85 memory fraction,eager mode. Root8192/child4096 output caps. Per endpoint:12 root iterations,36 plain child requests,48 physical requests total,120s worker cap; two endpoints concurrent. These are caps, not promised consumption or equal FLOPs. GPU fit/startup remains untested; estimated15.3GiB weights plus up to9GiB KV for two full contexts leaves working margin on40GB.

Actual generated code runs only in the qualified rootless container/image: no network, read-only root/source/dependencies/task mounts, no host project/home/models/credentials, dropped capabilities and bounded memory/PIDs. A Unix socket exposes only inference/events. Host recorder never executes sampled code. The actual historical worker uses Python3.11.16; host collector/launcher use qualified Python3.12.12. New pure-Python dependencies are installed only in a new external target and pinned. Container release receipts and exact-name interrupted-container reclamation are owned by this attempt; no unrelated cleanup.

Primary: strict whole stripped `Answer: N`, exact native final lineage, dataset correctness per24 planned/policy, plus availability and NULL bounds. Authenticated malformed finals are strict0. Missing/unreturned/final-less endpoints remain NULL, including policy loops; report operational zero sensitivity separately. A returned length-capped response can still produce a genuine complete final; length remains flagged. FINAL_VAR requires the actual retrieval observation and matching last native root response. Separate actual acquisition, executed evidence-dependent computation, nonzero successes, and mere literal/manual answers. No sampled-code replay in analysis. All physical attempts, prompt/output tokens where observed, unknown costs, errors, and outstanding requests remain separate. Provider billing is unknown.

## Time, persistence and launch limits

3600outer/3330work/3480owned: first policy≤1620, second≤1620,90finalization;150cleanup and120outer margin. Stages advance early. Each service startup≤150; collection stops30s before its policy deadline for ordinary service release. Cleanup can add20s per endpoint and service ownership escalation can exceed30s; therefore24 completed endpoints/policy are not guaranteed. An ordinary first-policy failure preserves the second reservation, but MAIN cancellation or owned deadline never launches a later policy. Both weights are frozen independently of ongoing SFT.

All48 NULL rows are planned before startup. Every request/response, native validation, REPL event and episode result is checkpointed. Owner harvest is coordinate-wise: a missing aggregate never erases completed episode results or physical calls. No rerolls, in-place resume, checkpoint selection, or automatic second attempt. Interrupted partial artifacts are retained for independent audit.
