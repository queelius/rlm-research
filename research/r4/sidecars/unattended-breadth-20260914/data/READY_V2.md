# READY — breadth screen v2 (sealed pilot input)

The pilot owner has launched from `cases-v2.jsonl`; do not rewrite it or `prepare_v2.py`.
Its immutable SHA-256 is
`356301e5a85a420ed1b740208031b3dbcb9cd5018fac57618bd392e83b144783`.

v2 contains 2,277 host-scored cases: 512 answerable MuSiQue dev, 512 FinQA dev,
512 BoolQ validation, 238 disjoint AG News count groups, and 503 LongBench v2 records.
`answer` is null and the runner should score only `metadata.gold`.

Important scoring seam: 508 retained FinQA targets are `number` strings and 4 are boolean.
In this exact slice there are zero percent-formatted and zero comma-formatted number strings,
but one scientific-notation number string. A float-only scorer needs an explicit conversion
policy before using that one item; this artifact intentionally preserves raw `exe_ans`.

See `MANIFEST_V2.json` for source indices, answerable-MuSiQue provenance, LongBench pin,
and the no-covert-exclusions receipt.
