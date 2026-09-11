# Independent partition final-interface audit

September 9, 2026. The syntax/domain grammar fixed the surface format but did not recover a correct
join: strict whole-response accuracy was **0/24**. All 24 planned calls are present, natively
authenticated and non-NULL. The 12 exact-decoder outputs are sorted, unique, in-domain arrays, but
all 12 are semantically wrong. The 12 free-decoder outputs are prose-wrapped and therefore fail the
whole-response contract. None used a native tool route, hit the length cap, or failed infrastructure.

| Input state | Decoder | Strict correct | Valid array but wrong | Malformed whole response | NULL |
|---|---|---:|---:|---:|---:|
| Full report | Free | 0/8 | 0 | 8 | 0 |
| Full report | Exact | 0/8 | 8 | 0 | 0 |
| Direct records | Free | 0/4 | 0 | 4 | 0 |
| Direct records | Exact | 0/4 | 4 | 0 | 0 |

Every free/exact source pair is tied at zero on the primary score. Exact decoding wins format
validity in all 12 pairs, but format validity is not task correctness. Across exact outputs, the
eight full-report calls contain 33 true-positive IDs, 17 false positives and 15 false negatives;
the four direct calls contain 13 true positives, 6 false positives and 11 false negatives. These
set diagnostics use only already valid whole-response arrays and never reorder or repair them.

## What this changes

This is a narrow instrument result, not evidence that information was lost between workers. The 24
historical extraction calls were reused unchanged and remain exact. The eight supplied full-report
states are theoretically sufficient to compute the gold joins, and the original 48 records remain
visible in every prompt. Free outputs contain extended task-relevant prose, but the audit does not
extract an array from that prose or award a repaired score. Exact decoding instead forces concise
arrays and exposes semantic errors. Thus the domain-only grammar solves the output envelope while
leaving—or changing—the model's selection policy.

Direct exact also fails in all four worlds, so full-report failure cannot be assigned specifically
to report composition or communication. The two full states for a world produce different exact
arrays in three of four worlds, which is descriptive evidence of supplied-state sensitivity, not
evidence that either state was used correctly. Only four engineered worlds underlie the 24 calls:
there are 12 unique prompt clusters, comprising eight full states and four direct worlds, with one
free/exact pair per source. Endpoint rows are not independent replications.

The prior partition audit's positive facts remain important counterevidence. It found exact
extraction in 24/24 calls, full-report sufficiency in 8/8 coordinates by deterministic projection,
and query-relevant facts retained in ordinary prose. This new result therefore should not be
summarized as “communication loss.” It says this released model plus this final-answer interface did
not convert available evidence into an exact join on these four worlds.

## Independent method and native evidence

The primary scorer accepts only a complete JSON array whose items are unique, sorted members of
`c01` through `c12`, then compares that array exactly with gold reconstructed from the 48 visible
records. It does not read the scientist's score, extract fenced/prose answers, sort, deduplicate,
execute tools, or infer missing entries. An authenticated tool route or capped/malformed completion
would be observed zero; missing, transport-failed or natively inconsistent output would be NULL.

All 24 returned responses authenticate against the frozen released Qwen3-4B-Instruct-2507 model,
the exact native prompt and completion token arrays, assistant choice/role/finish branch, decoded
text, and prompt/completion/total usage. Independent scores disagree with the scientist scorer on
0/24 calls. The paired request bodies are byte-equivalent in content and sampling fields except for
the exact arm's domain-only grammar. That grammar specifies only an array of customer IDs; it has no
gold IDs, cardinality, uniqueness, or sorting constraint.

The method timing is intentionally transparent. The exact strict-score, native-tool and NULL tests
were written before the owner started. The implementation and complete source closure were finished
after the run terminated, but before this auditor read any outcome content. This is an independent
exploratory audit, not a fully prospective or fully outcome-blind preregistration. The terminal
outputs were then pinned before parsing, and no result-dependent scoring change was made. A
post-outcome diagnostic only separates the frozen scorer's broad “observed strict failure” count
into 12 malformed responses and 12 valid-but-wrong arrays.

The run completed normally: 24/24 recorded and available, 94.3073 collector seconds, 131.4400 owner
seconds, clean release, and no retry. Native usage is 25,720 prompt and 13,800 completion tokens.
Summed request time is 319.3073 seconds. By cell, free generation used 13,350 completion tokens and
exact generation 450, making the format intervention materially cheaper here without making it
correct.

No new extraction was performed. The audit verifies 24 unique historical extraction calls
(7,056 input tokens, 5,448 output tokens, 193.9091 summed request-seconds). Charging those same three
historical calls to each of the 16 full endpoints yields 48 hypothetical acquisition calls. That is
a standalone endpoint accounting convention, not 48 new calls and not physical compute to add to
the 24 historical calls. This study made 24 new final calls.

## Ranked next comparisons

1. **Test the final-role/interface package before changing evidence.** On fresh worlds, cross a
   final-only classification system and no-tools interface with free versus exact decoding for
   matched direct and full-report inputs. The concurrently prepared leaf role/tool study addresses
   this mechanism on a different classification task; use its result to retire redundant cells.
   Preserve whole-response accuracy, valid-but-wrong arrays and prose/tool routing separately.
2. **Establish a deterministic reduction baseline.** Feed the exact extraction arrays to a pinned
   host reducer on fresh worlds and compare its end-to-end result and cost with the LLM final step.
   If deterministic composition is reliable, use the LLM where language understanding is needed
   and stop asking it to perform a fragile set join.
3. **If an LLM final step remains necessary, compare representations with facts fixed.** Match raw
   extraction arrays, per-customer incidence, and the current full prose report under one qualified
   final-only exact interface. Rotate presentation order and use genuinely new world clusters. This
   can test state-use/interference; another seed on these four worlds is only seed robustness.

Do not prioritize wider extraction, a communication-loss claim, or training from this result.
Extraction is already exact here, direct inference also fails, and the interface package has not yet
been isolated from semantic reduction.

## Seals

- Accepted science `READY_V2.json`: `99cc501ecd84b10917045fa2b38a34cf8181ab8c3cf3c9b35c6a5d452493fafe`
- Accepted science identity: `f4d1f94bb83ea81efd45a5424cbf8dcdb6d91ba564d8a393c9578080ab3c3ed0`
- Audit `METHOD_READY.json`: `e24c68235184d02f811eed0a87cbb3be8478177f238c5e205db93c9e1309465f`
- `OUTCOME_PINS.json`: `d20b7f41b3d08cfde4741aedffc053bcc945dc0f22da50686336bc0e37906a14`
- Independent `AUDIT.json`: `03958de75854c49638c53f230125c0774ae442c9f5c9c3ab0ec414ade5db128d`
- Post-outcome `DIAGNOSTICS.json`: `239c122294f7245e48796e797f2746b74bd7160d5b02ef691a2e0f59f8486848`
- Science `OWNER_TERMINAL.json`: `37a90c8fda013c53e94a472bb01b181a576d1e5b7c16a062574f1308847e3b47`
- Science rollout `STATUS.json`: `d1ebf2fdd8551d233af67da585e5a631e697da8c34399e49d9db9d5326c0e8a8`
- Prior independent partition report: `6d72da758a4d69561445b1799a7d78662550c948c92da5f687745f9016c7206a`

Audit artifacts live in
`/project/alex_phd/runs/rlm-research-r4/analyses/root-partition-final-interface-live-2026-09-09`.
Science outputs and prior reports were read-only; this audit made no GPU, model, service, lock,
queue, or source changes.
