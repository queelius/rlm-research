# Explicit output IDs recover large-batch correspondence across two tasks

Completed anchor control, independently audited on 2026-09-09. Indexed SFT is running and is **not** part of this result.

## What happened

With the same old TREC-trained child (`c32de…`), mapping labels back to explicit input IDs greatly improved 64-item classification. This held on six exposed TREC contexts and four new SST-2 sentiment contexts. Both output representations used the same indexed question/sentence input, exact-cardinality schemas, and a common 3,072-token output cap. Every response was valid; the gain therefore cannot be explained by rescuing invalid arrays in this comparison.

| Task / batch size | Anonymous labels | Indexed labels | Coverage |
|---|---:|---:|---|
| TREC / 64 | 586 / 1,536 (38.2%) | 1,437 / 1,536 (93.6%) | Both 24/24 complete valid contexts |
| Fresh SST-2 / 64 | 615 / 1,024 (60.1%) | 986 / 1,024 (96.3%) | Both 16/16 complete valid contexts |
| TREC / 5 | 738 / 768 (96.1%) | 736 / 768 (95.8%) | Both 12/12 reconstructed contexts valid |
| Fresh SST-2 / 5 | 485 / 512 (94.7%) | 491 / 512 (95.9%) | Both 8/8 reconstructed contexts valid |

These denominators include repeated seeds and, at size64, two permutations. They are not independent test-question counts: TREC has384 unique questions in six contexts; SST has256 unique sentences in four contexts. Size5 has one permutation and includes each context's final four-item residual batch.

All24 TREC and all16 SST size64 paired coordinates improved. Within the same item/seed/permutation, TREC gained881 correct assignments and lost30; SST gained380 and lost9. Each of the six TREC source contexts and four SST source contexts improved when its repeated observations were aggregated. Small-batch changes were modest: TREC seven gains/nine losses; SST seven gains/one loss. See [all paired outcomes and raw-file hashes](../../../../ARTIFACTS.md#unpublished-files "Not published: ANCHOR_METRICS.json").

## The late-position collapse largely disappears

Correct assignments in successive blocks of16 input positions:

| Task | Anonymous | Indexed | Denominator per block |
|---|---|---|---:|
| TREC64 | 319,101,68,98 | 374,355,359,349 | 384 |
| SST64 | 217,130,133,135 | 241,249,251,245 | 256 |

This supports a correspondence/representation explanation more strongly than a lack of small-batch task competence: the same weights classify small batches well and retain high late-position accuracy with explicit output IDs. It does **not** identify a particular attention or memory mechanism.

High item accuracy still is not exact aggregate reliability. Only1/24 indexed TREC64 responses had every label correct; indexed SST64 had0/16 perfect responses. Anonymous64 had no perfect responses on either task. A downstream exact-count task may therefore remain difficult even after the correspondence failure is substantially reduced.

## What was verified

The independent [audit program](../../../../ARTIFACTS.md#unpublished-files "Not published: audit_anchor.py") recomputed predictions directly from all600 raw response bodies, rejecting malformed arrays, duplicate/missing/extra IDs, and non-string values. All600 recomputed score vectors and primary correct counts match the stored scores. There were no HTTP/episode capture errors and no length stops.

For all600 calls, the captured HTTP body bytes equal the frozen bound request serialization, the actual response model equals the bound old-child alias, provider prompt-token IDs match the frozen typed-template qualification hash, and provider prompt usage equals the captured token-ID length. Every prompt plus its output cap fits8192. This audit compares the actual IDs with the qualified IDs; it does not claim an additional independent tokenizer implementation. All1,200 raw call/wire files and salient completed manifests are hashed in `ANCHOR_METRICS.json`.

Collection completed600/600 in175.643 seconds, with no unrun coordinates. Actual total usage was617,172 logical input tokens and54,810 completion tokens. The service wrapper took225.599 seconds including startup/cleanup; its owned-release marker was written, GPU process listing was empty, and indexed SFT then started automatically at02:48:22 UTC. The preceding root wait was1,405.112 seconds and is not counted as anchor compute. Primary [status](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-correspondence-anchor-transfer-v1/outputs/attempt-001/STATUS.json"), [aggregate](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../sidecars/leaf-correspondence-anchor-transfer-v1/outputs/attempt-001/analysis.json"), and [owned-stage exit](../../../../ARTIFACTS.md#unpublished-files "Not published: ../../operations/2026-09-09-queued-successors/attempt-001/anchor/EXIT.json") remain unchanged.

## Limits and the next discriminating question

This is task transfer beyond TREC's six output labels: SST uses positive/negative sentiment on256 groups excluded from the earlier SST study. It remains public labelled validation with unknown pretraining exposure and no independently confirmed underlying-data license. TREC contexts have been exposed in earlier experiments. There is one child checkpoint, only six/four source contexts, two seeds, and no blind test or end-to-end RLM intervention here.

The intervention changes the output instruction and grammar as well as emitted IDs. It is not an isolated input-ID test: both arms already have indexed inputs. Indexed64 consumed17,101 versus5,416 output tokens on TREC and10,256 versus3,088 on SST—roughly3.2–3.3 times as many. Thus the common maximum cap does not make actual generation compute equal, and fixed-ID grammar anchoring remains a plausible contributor.

The next useful distinction is **learned, unconstrained correspondence versus grammar-supported correspondence**. The already frozen indexed-SFT job tests free-output old/B/new readouts on identical prepared bodies within representation; its result must be awaited separately. A small subsequent matched free-versus-schema comparison on new source groups could determine whether IDs work without grammar and whether the trained model transfers this behavior beyond TREC. That is a proposal, not launch authority or an adaptive change to the running job.
