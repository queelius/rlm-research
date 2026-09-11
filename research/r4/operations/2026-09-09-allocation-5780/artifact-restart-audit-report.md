# Independent artifact-restart audit

September 9, 2026. Quoting the genuine pre-correction transcript made the old predictions usable;
merely placing the same state in files did not. Strict accuracy was **10/16 for quoted history
(Q), 3/16 for artifact reference (A), and 6/16 for metadata (M)** on the planned denominator. M had
two native length-capped completions with no final answer, so its conditional score is 6/14 and its
frozen-protocol range is 6–8/16. These are 16 paired source states over only four previously exposed
context clusters, not 48 independent contexts.

| Restart representation | Correct / planned | Available | Actual prior-state use | New child reacquisition |
|---|---:|---:|---:|---:|
| Q: transcript quoted in new user message | 10/16 | 16/16 | predictions incorporated 15/16; faithful scoped result 12/16 | 0 calls |
| A: files named, content not inline | 3/16 | 16/16 | 0/16 state-file reads | 42 calls in 13/16 rows |
| M: public metadata inline, maps remain files | 6/16 | 14/16 | 2/16 map reads; faithful scoped result 1/16 | 0 calls |

Within the 16 matched states, Q beat A in nine, tied in five, and lost in two. Among the 14 states
where M returned a final, Q beat M in five, tied in seven, and lost in two. These descriptive paired
counts preserve source-state dependence and do not turn four underlying contexts into independent
replications.

## What the traces show

Q did more than echo a scalar. Twelve programs reconstructed the complete 16-ID supplied map
exactly; four of those were width-4 states requiring all four historical map pieces to be combined.
One additional program used the supplied target-ID set without materializing a dictionary. Across
all Q rows, 15 incorporated actual historical predictions, and 12 produced the exact scoped count
implied by those predictions. Three incorporated the state but then made scope/correspondence
mistakes; one ignored it. The 12 faithful reductions yielded only 10 gold-correct answers because
two inherited child-prediction maps were semantically wrong. This is useful counterevidence: better
state uptake cannot repair wrong upstream classifications.

A never opened `state/history.json`, a map file, or metadata in any of its 16 fresh sessions. It
made fresh child calls in 13 rows instead: 42 calls total. Seven traces processed four batches by
reassigning `labels` each time and left only the last batch in the persistent variable; five of
those seven were width-4 states. One width-4 trace did merge all newly acquired batches, but failed
to apply the requested user scope. Five rows eventually requested only the relevant records; three
of those happened to be gold-correct. Thus A's 3/16 is reacquisition behavior, not evidence that
the archived files were used.

M mostly classified record text heuristically despite being told which map files existed. It read
the single width-16 map in only two traces. One detected and corrected its mistaken assumption that
map values were nested objects, then performed the right scoped count. The other displayed the
genuine map, treated dictionary iteration as if it yielded records, hallucinated user assignments,
and returned a prose-wrapped answer; the audit neither repaired nor extracted it. Inline metadata
therefore did not by itself induce reliable retrieval.

Two observed outputs were strict failures rather than NULLs: one A and one M returned prose
around an answer. The two protocol NULLs were not transport failures: both were authenticated M
responses that consumed the 2,048-token cap and left empty final content. They remain NULL under the
frozen scorer; treating any no-answer policy outcome conservatively as zero leaves the reported M
planned-denominator score at 6/16.

## Provenance, native evidence, and costs

The audit verified 200/200 new native calls with no mismatch in routed root/child adapter, response
model, finish branch, nonnegative usage, first native prompt, or final prompt/completion branch token
arrays. The 48 episode hashes match their rows, and independent strict scoring disagrees with the
scientist score on 0/48 endpoints. New-call usage was 348,744 input tokens, 23,532 output tokens,
312,128 cached input tokens, and 36,616 uncached input tokens. This comprises 158 root turns plus
the 42 A-arm child calls; Q and M made no new child calls.

The archived evidence came from 40 unique historical paid child calls, not 120 new calls. Their
physical usage was 37,340 input, 2,430 output, and 34,528 cached tokens, with 28.2435 summed child
request-seconds. Charging one or four source calls to each hypothetical standalone endpoint would
produce 120 reused acquisitions, but that is an accounting convention and must not be added as
physical work. Source capture took 280.9848 gross seconds across the 16 authored histories; the
pre-correction observed spans sum to 59.2938 seconds. CPU verification/export and tokenization took
60.0924 seconds. The new collector took 415.0326 seconds; the owner took 459.8675 seconds and
released cleanly. These wall measures overlap or have different boundaries and are reported
separately, not summed.

All 201 pinned source files still hash correctly. For all 16 states, each packaged map is byte-equal
to its actual pre-correction tool observation and `history.json` is the exact cut message sequence.
The cut contains no nonempty provider state or reasoning content; package schemas contain no host
gold, later correction, final, or restored kernel. All 48 fresh runtime setup attestations match the
canonical package, records, context, and query hashes. The 40 historical child captures are unique
and returned. Accordingly, this tests fresh restart representations, not native continuation.

The audit method was frozen after the run had launched and after all outcome files existed, but
before this auditor read scores, finals, or model programs. That is a transparent independent
post-collection audit, not a prospective preregistration or a claim of full outcome blindness. The
output tree was pinned before parsing; manual data-flow judgments use only pinned executed programs
and returned observations, never execute model code, and do not infer execution from mentions.

## Ranked follow-ups

1. **Isolate observation visibility from program imitation.** On genuinely new contexts, cross
   inline map observations present/absent with the producer program quote present/absent, while
   keeping identical files and final interface. This distinguishes “the labels were visible” from
   “the historical code taught the merge.” A 2×2 matched design is more discriminating than another
   Q/A/M seed on these four contexts.
2. **Test retrieval as the intervention.** Compare file-only state with an otherwise identical
   condition whose first tool return supplies the same file bytes. Preserve retrieval, merge,
   scope, and gold accuracy as separate outcomes. This asks whether failure is choosing to read or
   using what was read.
3. **Use deterministic composition when classifications already exist.** A host merge/filter/count
   baseline would remove the observed last-variable and scope failures. If it succeeds, reserve the
   LLM for classification and stop paying for fragile reacquisition/composition.

Do not call this a global persistence or communication result. Q changes the new user message and
includes both producer code and observations; M changes inline metadata; A leaves content behind a
tool action. The experiment identifies a strong interface-dependent uptake pattern on four reused
contexts, while preserving contrary evidence from wrong upstream maps, Q scope failures, M's one
successful read, and A's three successful fresh reacquisitions.

## Seals

- Accepted science `READY.json`: `9568ab66b89269da8670b855e66e9db0c1122b8ddc196f5759afa931613f5b42`
- Science `OWNER_TERMINAL.json`: `874d67585b29c6bdee35fec48a60d1e7615516d538e8ecfeebb6eb3d2f2b0c91`
- Science rollout `TERMINAL.json`: `976d5acff409599896e0c7ba9f82a6dd284f296bd3a18de6ce3ba3c504818788`
- Audit `METHOD_READY.json`: `e08f7c9a4b424ce977888009f33d1a010bb0d584eaf1af3f4eb73c77c22d5dfc`
- `OUTCOME_PINS.json`: `ea9a08d616785b749bd11397abd95a17cd33d789a57a538a3e0887d93d67c3f2`
- Independent `AUDIT.json`: `c30d0e6d9a3d9d48f7a39b0bc51654cd3acef2605581f68665ad526da9ea6f5d`
- `PROVENANCE_AUDIT.json`: `257d602fecdf6f9ec11b5007e870fb383747e66eb8373d41b16761c4f12577ae`
- `DATAFLOW_AUDIT.json`: `5d657ab07c5189ae30727ed8c12b121f8c6eddae325009064f914d4c3c18880e`

Audit artifacts live in
`/project/alex_phd/runs/rlm-research-r4/analyses/root-artifact-restart-live-2026-09-09`.
Science outputs and sources were read-only; this audit made no GPU, model, service, queue, or lock
change.
