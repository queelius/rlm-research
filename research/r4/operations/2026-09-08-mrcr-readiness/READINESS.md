# MRCR cache and safe next-run proposal

The cache is available: five MRCRv2.1 CSVs, approximately1.7GiB, all present at manifest byte sizes.
The short2-needle4K–8K file is2,492,336 bytes, SHA81f5e08995cbf2c1d55947a80cb71ce1a62743819c0b48b85b4d4d3b30e725f5,
and its82 parsed rows were verified. The official scorer still matches SHA8d96a13b... and the
Google DeepMind eval_hub checkout is the pinned67b7fd29b2205ee0a3226e0d3e5d74140a253b42 commit.
No downloads or environment changes are needed for this follow-on.

Historical `mrcr-context-sketch-v1` must remain unlaunched under its old descriptor. It pins a
different Qwen3.5-4B model,262K direct context, and host `rlm serve` with unsandboxed generated
Python. Its prepared attempt has contexts, requests, sketches and seal, but no ledger/checkpoint/
result artifact was found. This is preparation, not completed research evidence.

The short band has82 questions but only SIX unique context bodies, with24,14,12,12,10,10 questions.
`CACHE_REPORT.json` retains the initial row-based draft for transparency; it is superseded by
`GROUPED_PROPOSAL.json`, selecting one question per document using fixed document/question hashes
and rotating answer-position quartiles. No model outcomes were read. Raw queries are4,526–7,928
Qwen3 tokens (median6,299); some cannot fit a complete direct answer inside an8K endpoint.

Smallest proposed comparison: six novel documents, one fixed question each, paired vanilla
file-backed RLM versus the same frozen policy/caps plus the existing task-blind context sketch.
Twelve episodes, temperature0, six turns/two subcalls/eight total model calls maximum,2,048 output
tokens per call,180seconds per episode,30minutes total. Record every terminal episode, actual
inspection and subcalls, official SequenceMatcher score, strict exact match, and failure category.
This is an exploratory task-transfer/harness baseline, not the historical confirmatory study or
training. Bind the actual parent-selected checkpoint before launch; using a different model must
remain explicit.

Reuse the newly qualified per-episode rootless boundary, not the old host RLM server: mount exactly
that episode's contextfile read-only; mount harness/source/interpreter read-only; keep only scratch
writable. Do not mount the dataset CSV or gold answer. Score only the completed returned terminal
prediction on the host; do not add an answer-file/last-message fallback. The cached official Prime
MRCR taskset is a useful source reference, but its taskset/client/reward bindings differ from the
qualified strict OOLONG path and should not be swapped without an additive driver/manifest.

The proposal is NOT launch-ready yet: it needs that additive contextfile worker/driver, exact
checkpoint binding, and a fixed rootless context-read probe. A direct reference is deferred unless
an explicit16K-or-larger endpoint and actual rendered-token counts are declared; do not truncate.
