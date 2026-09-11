# Independent audit: native partition join

Audit cutoff: 2026-09-09 22:25 UTC. The 48-endpoint run completed and released. The
source-informed audit method was frozen after collection had ended, but before this auditor read
any outcome field. This is outcome-blind post-collection scoring closure, not a prospective
preregistration.

## Answer

The run answers only the direct-evidence/tool-interface part of its question. Python availability
changed exact answer shape from 0/8 valid finals to 8/8, and produced 2/8 correct joins versus 0/8
without Python. All eight Python-present roots executed input-dependent aggregation and observed a
result; none delegated to a child. Six implementations nevertheless parsed the sentence format
incorrectly and returned an empty array. Python therefore made the released base operationally
capable of exact-form joins, but did not make the join reliable.

The co-located versus cross-partition root comparison is unanswered. All 32 report endpoints were
prospectively gated before root inference because no world/representation had three exact source
reports. This is not evidence that partition layout hurts the root. It is evidence that the
unconstrained extraction interface was unsuitable for a complete-report factorial.

## Results

| representation | Python | planned | source available | native finals | valid arrays | correct |
|---|---:|---:|---:|---:|---:|---:|
| direct originals | absent | 8 | 8 | 8 | 0 | 0 |
| direct originals | present | 8 | 8 | 8 | 8 | 2 |
| co-located reports | absent | 8 | 0 | 0 | 0 | NULL |
| co-located reports | present | 8 | 0 | 0 | 0 | NULL |
| cross-partition reports | absent | 8 | 0 | 0 | 0 | NULL |
| cross-partition reports | present | 8 | 0 | 0 | 0 | NULL |

The two correct Python joins came from world 2 repeat 1 (gold cardinality 7) and world 3 repeat 0
(cardinality 9). The other six Python rows returned the strictly valid but wrong array `[]`.
Python-absent rows all returned explanatory prose rather than the required bare JSON array; these
are observed contract failures, not NULL and are not repaired by extracting an embedded answer.
The paired direct comparison is therefore 2 Python wins, 0 losses, and 6 both-wrong pairs over four
world clusters and two paired seeds. Seeds within a world are not independent replications.

## Source gate

All 24 extraction requests were physically attempted and returned a native, shape-valid JSON array.
Only 5/24 preserved the complete 16-record chunk. The other 19 were strict subsets with no invented
extra rows, omitting 200 records in total. Every non-exact response contained only purchases of the
two queried products: 14/19 were the complete query-product subset and 5/19 omitted additional
query-product records. Only world 2's cross-partition trio was complete with respect to relevant
products, and even it was not complete with respect to the declared all-record extraction contract.

An explicitly post-outcome diagnostic merged the returned subsets and applied the trusted host
join. Despite failing the declared all-record contract, 6/8 world/representation packages still
implied the correct answer for this query; world 1 cross and world 2 co-located each omitted a
necessary query-product fact. This does not rescore any root or establish report usability, but it
shows that source-contract failure was often not communication loss for the current query.

Accordingly, exact full-report packages were 0/8 world/representation combinations. The frozen gate
correctly left all report roots unexecuted and all 32 report outcomes NULL. Trusted host reduction
of the original records remained correct for 4/4 worlds. No host answer or host-reduced report was
shown to a model.

This contract failure is mechanistically informative: despite an explicit instruction to preserve all
records and distractors, the final-only extractor mostly performed relevance filtering. Changing
the gate after seeing that behavior would alter the experiment; this audit does not do so.

## Native behavior

Every Python-present direct row embedded the visible evidence in generated code and performed an
across-record set aggregation. There were 12 generated programs and 12 observations across the
eight rows; no program opened the duplicate evidence file. Thus the observed factor is a native
Python-execution package effect, not file-access evidence. No root made a subordinate child call.

The two correct rows used regex parsing that preserved customer and product fields. The six empty
answers came from concrete parsing bugs: lowercase-only product regexes against uppercase product
symbols, splitting on text that did not occur, retaining punctuation in product names, or failed
first attempts followed by another parser that still yielded an empty set. These are observed
policy/program failures. Python was useful for output discipline and aggregation, but generated
parser correctness is the bottleneck.

Python-absent roots had an empty native tool inventory and made one root request each. They produced
long manual analyses rather than the exact contract. Python-present roots had the advertised
IPython tool, made 20 root requests in total (tool-action continuations included), and made no child
requests. There were no unadvertised tool attempts.

## Authentication and costs

Independent recomputation matched all four frozen host answers. All 24 acquisitions passed native
model, token-ID, and usage authentication; independent no-repair parsing reproduced the recorded
5 exact / 19 subset split. All 48 planned result rows were present. For all 16 executed roots, the
actual model alias, per-condition tool inventory, first message/tools/token prefix, fresh-runtime
file attestation, every trace-linked wire request/completion, final branch token identity, finish
route, and independent strict score matched. The remaining 32 were source-gated before native root
execution.

Physical work was 24 acquisition requests plus 28 root-pipeline requests, 52 total. Recorded usage
was 62,954 input and 28,208 output tokens; acquisition accounted for 9,216 input and 3,568 output
tokens. Acquisition wall time summed to 81.66 s, collector time was 257.70 s, and owner time was
297.77 s including service lifecycle. The ledger also retains 96 hypothetical per-endpoint report
acquisition charges, but those calls were not physically repeated. Provider billing was not
measured.

## Interpretation and next run

The positive result is narrow but useful: exposing native Python eliminated final-format failures
and enabled two exact joins without child assistance. The negative result is equally clear: an
unchanged coding model copied the prompt evidence into brittle parsers, and the report producer
systematically optimized for relevance instead of completeness.

Ranked follow-ups:

1. Run a small matched parser-interface test on fresh direct worlds: raw sentence evidence versus
   already structured triples, crossed with Python. This distinguishes aggregation difficulty from
   avoidable sentence parsing while preserving the same join.
2. Rebuild the report source contract prospectively. Either use a grammar/validator that guarantees
   all 16 triples or explicitly define query-relevant extraction and require complete relevant-row
   coverage. Then rerun co-located versus cross partitions; do not reuse today's gated NULLs as if
   roots had seen reports.
3. Only after source availability is restored, test whether file-native loading changes the current
   literal-copy strategy. The present run supplies no evidence that the model used files.

## Audit artifacts

Machine-readable evidence is under
`analyses/root-native-partition-join-live-2026-09-09/`: `METHOD_READY.json` and `AUDIT.json`,
with `freeze_method.py` and `audit.py`. `FINAL_MANIFEST.json` seals the report and terminal science
artifacts.
