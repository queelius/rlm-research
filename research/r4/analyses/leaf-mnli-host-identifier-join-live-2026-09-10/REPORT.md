---
id: leaf-mnli-host-identifier-join-independent-audit
status: sealed_independent_exploratory_audit
study: mnli-host-identifier-join
created_utc: 2026-09-10T17:34:21Z
planned_endpoints: 48
native_authenticated: 48
primary_mean_did: 0.484375
frozen_advance_gate: passed
owner_terminal_sha256: 75e704ee1651d18fa0e66d54aff0841aca5b8936b05e8a1ef52df483807f1576
parent_exit_sha256: f099f1641d2dc9ac90ba7e172e3e1b220afeffc69a8e47a4d30f1098780fed33
---

# Host attachment strongly changes the reference interaction, but is not a universal accuracy win

Moving identifier attachment into ordinary code passed the frozen exploratory screen. The
label-only minus tag-first effect was +14.1 percentage points under misleading identifiers and
-34.4 points under aligned identifiers. Their primary difference-in-differences was therefore
**+48.4 points**, positive and at least +10 points in all 8/8 exposed context clusters, with no
availability loss. This is strong evidence that requiring the model to emit the identifiers is
part of the measured reference interaction.

It is not evidence that label-only output is unconditionally better. Label-only accuracy fell
sharply when visible identifiers were aligned or unrelated. The intervention bundles natural
instructions, schema shape, output length, and identifier generation; host attachment itself is
deterministic and cannot repair a wrong semantic label. The result promotes host attachment as a
promising harness strategy for decoupling labels from misleading addresses, while demanding a
fresh-context replication and a mechanism control before general deployment.

## Independent native results

| Visible reference | Tag-first | Label-only + host join | Label-only − tag-first |
| --- | ---: | ---: | ---: |
| Misleading | 148/384 (38.5%) | 202/384 (52.6%) | +14.1 pp |
| Unrelated alien | 316/384 (82.3%) | 190/384 (49.5%) | −32.8 pp |
| Aligned | 318/384 (82.8%) | 186/384 (48.4%) | −34.4 pp |

Every cell had 8/8 native finals, 8/8 valid whole-output contracts, and no NULLs. All tag-first
calls copied all 384 expected tags in position. Identifier fidelity is deliberately not applicable
to label-only calls: the model emitted no identifiers, and the host joined each complete
48-label array to the frozen positional requested-tag list only after validation.

The eight primary context DIDs, in context order, were +41.7, +27.1, +35.4, +50.0, +60.4,
+62.5, +52.1, and +58.3 percentage points. Thus the frozen requirement of at least +10 points in
six contexts was exceeded in all eight. This is a practical screen, not a significance test.

The unrelated-versus-aligned secondary DID was only +1.6 points on average, with context values
from -16.7 to +12.5 points. That supports the interpretation that the large primary effect is
selective to misleading named records, rather than a generic advantage over both non-misleading
conditions.

## Wrong-named-record diagnostic

Across the same 258 label-disagreement positions per output format, tag-first predictions followed
the named record on 179 items, the displayed record on 43, and a third label on 36. Label-only
predictions followed the host-attached named record on 60, the displayed record on 139, and a third
label on 59. This diagnostic aligns with reduced named-record capture, although those 258 items are
nested within eight exposed contexts and are not independent trials.

## Availability, cost, and provenance

All 48 planned call directories contain requests, HTTP 200 responses, choice payloads, and
independently authenticated native finals. Exact ordered request bodies and hashes matched their
frozen copies; prompt token IDs, completion token IDs, token counts, model alias, and decoded text
matched. The independent scores agree with producer scores on all compared applicable fields.
There are no unexpected call directories, length caps, authenticated contract failures, or unknown
usage receipts. The live service identity matches the frozen Qwen3-4B-Instruct-2507 base model,
no adapter, vLLM 0.28.0, 8192 context, four sequences, bfloat16, and prefix caching disabled.

| Format | Calls | Input tokens | Output tokens | Sum endpoint elapsed |
| --- | ---: | ---: | ---: | ---: |
| Tag-first, all references | 24 | 91,758 | 23,432 | 553.29 s |
| Label-only, all references | 24 | 91,566 | 3,854 | 95.70 s |
| **Total** | **48** | **183,324** | **27,286** | **648.99 s** |

Cached tokens are zero. Label-only used 83.6% fewer output tokens and 82.7% less summed endpoint
latency than tag-first on this run. Endpoint times overlap under four-worker execution, so their
sum is not wall time. Provider billing and exact FLOPs are unknown, and an HTTP receipt alone does
not prove GPU execution; the 48 native choices are authenticated. The owner recorded 172.46 s for
collection and 209.55 s overall.

Before any outcomes were read, the exact owner marker was verified complete and released with
48/48 results, no errors, and SHA-256
`75e704ee1651d18fa0e66d54aff0841aca5b8936b05e8a1ef52df483807f1576`. The exact parent EXIT has
exit code 0, `timed_out=false`, no GPU PIDs after exit, and embeds that same owner hash; its SHA-256
is `f099f1641d2dc9ac90ba7e172e3e1b220afeffc69a8e47a4d30f1098780fed33`.

## Limitations and decision

These are eight research-exposed wording-control contexts sharing only 128 premise groups, one
model, one task, and one seed per context. Records, labels, and seeds are not exchangeable
replicates. The result is exploratory and should not be promoted to a general model claim.

Advance the harness strategy to a new-group replication, but do not deploy label-only as a universal
replacement based on this panel. The most decision-relevant next comparison holds label-only output
fixed while removing or neutralizing redundant input identifiers, then repeats on fresh MNLI groups
and another task/model. That separates reduced identifier emission from the surprising semantic
collapse under aligned and alien references.
