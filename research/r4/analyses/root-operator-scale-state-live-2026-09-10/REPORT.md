# Independent nested scale/state24 audit

**Fixed24 scores4/8 at16 records,0/8 at128 and0/8 at256.** All four successes genuinely execute the requested reduction on actual child labels. No executed multi-acquisition accumulation was verified. Two256-record paths acquired predictions covering all256 records in disjoint batches, but repeatedly overwrote the same state variable rather than accumulating it. Thus acquisition feasibility and successful evidence use are distinct bottlenecks.

## Planned scores, availability and dependence

All24 endpoints were attempted. Nineteen have RESULT files, twelve have authenticated native finals; all twelve finals satisfy the unchanged strict `Answer: N` format. Missing RESULT/no native final stays NULL, never salvaged from program output or raw transport. Operational no-final failure is unsuccessful, while native-answer bounds retain uncertainty.

| Records | Correct / planned | Native available | Correct / available | Native-answer bounds /8 | Count correct /4 | Weight correct /4 |
|---|---:|---:|---:|---:|---:|---:|
| 16 | 4/8 | 8 | 4/8 | 4–4 | 2 | 2 |
| 128 | 0/8 | 4 | 0/4 | 0–4 | 0 | 0 |
| 256 | 0/8 | 0 | undefined | 0–8 | 0 | 0 |

At128, three count finals and one weight final are available; at256 neither operator has a final. All24 source-gold values are nonzero. Zero baseline0/24; predeclared pooled best-constant baseline40 scores2/24. No zero/answer selection or reroll was introduced.

Each parent contributes two tasks per size. Cells show **correct / available /2**:

| Parent | 16 | 128 | 256 |
|---|---|---|---|
| scale-state-00 | 2/2/2 | 0/1/2 | 0/0/2 |
| scale-state-01 | 0/2/2 | 0/1/2 | 0/0/2 |
| scale-state-02 | 0/2/2 | 0/1/2 | 0/0/2 |
| scale-state-03 | 2/2/2 | 0/1/2 | 0/0/2 |

Operational128−16 and256−16 differences are−4/8, with two negative and two tied parent means.256−128 is operationally tied. Conservative aggregate native-answer difference bounds are[-4/8,0] for128−16,[-4/8,+4/8] for256−16, and[-4/8,+8/8] for256−128. Exact eight paired parent/operator blocks and their individual bounds are in [NATIVE_AUDIT.json](../../../../ARTIFACTS.md#unpublished-files "Not published: NATIVE_AUDIT.json"). Only four parent clusters exist; no independent-record/seed inference, complete-data bootstrap, equivalence claim or universal memory-capacity ceiling is justified.

The intervention changes the number and content of nested records under fixed caps: it tests the whole size/state burden, not memory alone. The1024 groups were root-new under the frozen named inventory, but child-training/catalog exposed, with familiar task operators. Actual nested IDs/order/users/weights and all24 deterministic golds were independently checked against the frozen source inventory. No global-unseen claim is made.

## Actual computation and failure mechanisms

All twelve available program/observation sequences were manually reviewed; remaining paths were reviewed through recorded traces and authenticated raw branches, including decoded actual subsequent request histories for missing-RESULT paths. No sampled program was reexecuted. [EVIDENCE.json](../../../../ARTIFACTS.md#unpublished-files "Not published: EVIDENCE.json") contains all24 exact coordinates, full available programs/observations, actual maps, failed-request histories, per-row notes and raw paths.

Eight finals genuinely reduce the requested complete live map: the four correct16-record answers, one wrong16-record weight sum, and three wrong128-record counts. The latter four wrong answers are explained by actual child semantic errors for those correctly executed operations:

| Context/task | Dataset answer | Actual complete-map reduction/final |
|---|---:|---:|
| parent01,16 weight/entity | 21 | 23 |
| parent02,128 count/location | 19 | 17 |
| parent00,128 count/human | 35 | 31 |
| parent01,128 count/entity | 26 | 40 |

Extra nonexistent user names in some filters are inefficient but cover the full actualu0–u3 universe; they are not treated as omitted scope. Four other available finals are root-computation failures:

- `1cdb109a97…`, parent01/16 count: complete16 map replaced by first8 then last8. A KeyError is “repaired” by checking map membership, silently counting only the last half:4 rather than gold5. Earlier complete-map agreement is not evidence of actual accumulation.
- `333e86e934…`, parent02/16 weight: omitsu3, yielding14 rather than20 despite complete-map requested sum20.
- `8880ab47ad…`, parent02/16 count: omitsu3 and sums weights instead of counting, yielding14 rather than4.
- `2c4ce2fec3…`, parent03/128 weight: omitsu0, yielding62; the requested full-map sum is84 and dataset answer89. Both source semantics and root scope contribute.

Seven endpoints issue at least two child requests, but none demonstrates two useful contributing acquisitions in an executed accumulated reduction. The decisive paths are:

- **Parent00/256 weight, `ce3050f74a8e9461ab718540d9799d8a47a61f84f7d02c61f382a4fc1c186c4b`:** sixteen disjoint16-record returned maps cover all256 records and are printed in actual observations. Every program assigns `chunk_map = strict_map(...)`, overwriting its predecessor. The next reduction tool is malformed; no final or executed accumulated reduction exists.
- **Parent01/256 weight, `80f77a33db…`:** eight disjoint32-record maps cover256. `chunk_labels` is overwritten on each batch. A full-record lookup then raises KeyError; the retained next root request includes that actual error and exceeds context at10,799 input tokens. This is not successful state accumulation or evidence that multiple acquisitions are impossible.
- **Parent03/256 weight:** two five-record maps are overwritten, then malformed tool output. **Parent01/128 weight:** seventeen singleton calls fail decoding because ordinal strings such as`'16'` are supplied instead of actual q-IDs. These calls do not become useful accumulated evidence.
- **Parent00/256 count:** a whole256-map child answer truncates near the context limit; repeated identical f-string SyntaxErrors follow, then an unclosed tool. **Parent03/256 count:** eight overlapping256→249-record requests return truncated maps (41→254 completion tokens, matching remaining8192-token context), then the root request is rejected. No partial-array rescue is applied.

These mechanisms favor testing retained, query-free evidence state and task-spec fidelity, not simply increasing child-call count. The observed complete disjoint acquisitions still establish no robust accumulation competence.

## Native identity, NULLs and cost

All24 first root native prefixes exactly match frozen token IDs. Actual fixed24 adapter`94022838…`, c32 adapter`c32de129…`, configuration hashes, service model directories/cards and pinned Qwen3-4B-Instruct-2507 base match the approved binding. Actual root/child requests use2048 action limits with8192 service context; roots retain .5 temperature and paired frozen seeds. All250 returned physical branches match typed request bodies, full token/logprob sequences, parsed messages/tools and finish semantics; all12 finals have unique exact-body/token joins and completed trace identity.

Twelve native NULLs comprise six sampled malformed-tool endings, five attempted timeouts after HTTP400, and one broker `_queue.Empty` after repeated category-field/decoding errors. The broker failure's causal attribution remains unresolved. Two HTTP400s are child requests with8367 input tokens; three are root requests with8477,10,799 and8443 input tokens. These exceed8192. Rejections are physical request attempts, not established GPU completions. The five absent RESULTs are attempted failures, not unstarted slots.

| Records | Physical attempts | Returned completions | Known input | Known output | Usage-unknown attempts |
|---|---:|---:|---:|---:|---:|
| 16 | 48 | 48 | 79,226 | 4,995 | 0 |
| 128 | 72 | 71 | 215,604 | 20,396 | 1 |
| 256 | 135 | 131 | 502,346 | 19,061 | 4 |

Total255 attempts,250 returned completions,797,176 known input and44,452 known output tokens; five attempts have unknown usage. Cached656,896 is part of input, not additional tokens. Child requests74, child returns72, at least one returned child in22/24 endpoints. Physical identities are unique and raw-ledger union includes every coordinate irrespective of RESULT. Billing is unknown; no unknown usage imputation.

Recorded SUITE_PREFLIGHT is model/version metadata GET work, not sampled generation. The source/retained artifacts establish no separate before/after generation preflight; no invented model cost is assigned to absent artifacts. Release/outer lifecycle receipts are retained separately. No new training or external acquisition occurs; historical checkpoint/data costs are reused provenance. Owner elapsed575.184s, outer575.662s, exit0/not timed out and GPU released, within2400s. Collection/owner clocks overlap and are not summed as kernel time.

## Closure and interpretation

The method was prospectively sealed before this run's outcomes. MAIN authorized reading after terminal; no other live experiment was inspected. The frozen inherited reader's known typed-UUID/provider-ID mismatch creates rejected preliminary availability, preserved in PRELIMINARY/NESTED_PRELIMINARY. [READING_AMENDMENT.md](READING_AMENDMENT.md) documents the separately tested exact-body/full-token correction, with distinct IDs retained. No score rule or historical file changed.

The finding is an operational scale failure of this exact fixed24/c32/interface/cap package, combining source-label errors, wrong task operations/scopes, overwritten state, decoding misuse, truncation and native tool/final failures. It is not evidence that execution tools cannot handle256 records. The smallest informative successor should isolate persistent acquired state from the unmodified access path, while separately scoring dataset correctness, faithful requested computation and actual accumulation. A loader that merely rereads raw records would not by itself preserve newly acquired predictions; that distinction must be explicit in any proposed intervention. Existing task-spec/scale diagnostics should inform the next training or harness choice before more dose alone.
