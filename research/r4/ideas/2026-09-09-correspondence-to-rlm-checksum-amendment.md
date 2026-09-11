# Proposed scalar-checksum amendment

2026-09-09; design-only, awaiting MAIN choice. Supersedes first-match retrieval in correspondence-to-rlm-next-options.md; no accepted source changes.

Retain32 episodes: query_transfer00/01 and length_transfer00/01 × count/checksum × two seeds × array/map children; fixed low66cce+c32, proposed981326001/011/021, balanced dispatch,1800s outer. Both tasks concern **all** records of the context's public target category. Count returns their number; checksum returns the sum of their numeric ID suffixes, with empty sum0. Both demand whole ASCII `Answer: N`. Full-scope semantic evidence is needed, but no helper/coverage requirement enters scoring: direct computation and freely chosen batches remain valid. Checksums expose many count-preserving misassignments, not all—different subsets can share a sum.

Root prompts, public API, worked example, weights and sampling are identical across representations within each task. Child definitions and ordered public ID/text records remain identical. Freeze two consistent output blocks before inference:

- Map: “Return only one JSON object mapping every supplied id exactly once to one label. No missing or extra ids.”
- Array: “Return only one JSON array of exactly N labels in supplied record order. No missing or extra labels.”

N is requested batch length. The same canonical-label list follows both; grammar enforces the respective exact map/array. This deliberately changes child instructions/action space, not root wording.

Audit chain: authenticate original public request+trusted invocation/depth → log actual child prompt/schema/native tokens → preserve raw child response/graph → broker-only zip-by-requested-order and identical canonical-map serialization → actual subsequent root input. Never replace sampled child tokens/logprobs with projected map text. Preserve semantic errors, malformed/unavailable returns and all32/null denominators; no gold repair or study retries.

Width evidence is limited: completed typed-operator maps at16 achieve727/768 and980/1024 source-label accuracy, but there is **no matched array control at16**; strongest correspondence contrasts used64. Thus positive headroom is plausible, not established. Report actual eligible width bins1–4/5–16/17–64/>64, uptake, syntax, coverage, child semantics, returned-map-to-scalar fidelity and costs separately by task/context. Do not force large calls or reinterpret small-batch null effects as refutation. Novel checksum arithmetic may hide a child benefit; component and whole-task outcomes remain separate. No queued outcomes were read; shifted-ID72 proceeds independently.
