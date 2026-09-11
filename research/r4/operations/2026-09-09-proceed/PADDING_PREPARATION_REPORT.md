# Padding control128 CPU preparation report

Prepared September9,2026, approximately04:15UTC. The bounded old-adapter-only
sidecar is CPU READY. No service/model/GPU calls occurred, no GPU processes were
signaled, no environment was installed or changed, and no parent acceptance or
active-chain source/manifests were written. `git status --short` was empty at the
final source check. The namespace has no `outputs/` or `owned/` attempt yet.

## Exact artifacts and identities

All sidecar paths below are under:

`/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-anchor-padding-control-v1/`

| Artifact | SHA256 |
| --- | --- |
| READY.json | 9a53e3d0d758a7235376e1e12f842d08b9197da081a6ffbc2162f1fda5350521 |
| SPEC.json | 90d3ed6ca7acfee9f5e5c3f3dae4000ac6fc1e0f2dacceeba5fd500d69cf1f94 |
| DATA.json | ae811a1d4f173315d00d22717551bafbad0517c4631e3d00c8efea316570f918 |
| REQUESTS.json | dbf3fb9fec1d8b6307d7b13ca27545e196eb79663699c3e3885673ee89598c73 |
| CPU_QUALIFICATION.json | 4144d8f12a8cfdba2cadd8576d337827a77503513ec6b9334a464869730849e8 |
| CPU_TESTS.json | 224b4478e74ea215d5bb034f96ceb7444e4a3fd5eceb72a39276069c37032645 |
| WEIGHTS.json | 084fa3609673a5bfa63e8f1a0013d70ade0de6ad96022bc4a54ebda066f08a92 |
| study.py | d8cc897b670929acc3b19c75ff9b01ee963afecf13935d92a426f88b14060a9b |
| driver.py | 045355caa4955addd1936cfb756b0ff35f8578492045cc41644c03ccc2cdbe83 |
| owned.py | 206e50a913727e0f66b6bb26002ff07ec75d7c763a4a23715f6e56c4cff65f53 |

SPEC identity is
`df94ac2a48af1d2cfcb955db6a3cd9781d4f78acdb93d6c38be18dfc754b1cc2`.
READY status is
`CPU_READY_128_FROZEN_SINGLE_OLD_ADAPTER_OWNED_LIFECYCLE_IMPORTED_NOT_LAUNCHED`.
DESIGN.md and README.md give readable design and launch instructions. SPEC pins
the complete inherited anchor source/input closure plus new source, data,
qualification, tests, seed audit and weight files. READY additionally pins the
owned wrapper and unchanged lifecycle suite/manifest. No source changes are
needed for endpoint binding: all128 requests already use the exact old alias.

Selected source DATA is:
`/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-indexed-grammar-transfer-v1/DATA.json`
with SHA256 `ca5a895f361d8a590078e36393c6edf900e86a6da7b17382440366581642e17f`.
Its SPEC pin is `c9bdead579cc6da8ae5910835f6c4742f2f1ed0121c42afcd397be1bc99e7f3b`;
study.py pin `861fae26e0b5bc6855b80c20a459cd1526e4bfd49b4e83fb3a380abb4a161487`;
driver.py pin `17d46458875e2fdbb3f03d951ef6659ae54165cb3d420b5f4678886eb1857f67`.
The inherited anchor study.py pin is
`5794187b8a6ab18a12103bd54a60bed8d55875e0292d74b2cfe082dbc9c02a00`.

## Frozen design

The first four declared TREC contexts and all four SST contexts retain their
exact64 input records, questions, IDs and order from grammar160. Original
grammar context indices are retained separately when local indices are assigned.
Seeds981264101/981264102 cross anonymous arrays, ID maps, meaningful-tag arrays
and constant-q0000 placeholder-tag arrays with free/exact-schema decoding:
128 calls,64 per task. Both seeds and all requests were frozen before inference.
No labels or outcomes affect context selection, permutation, IDs or prompts.
The later Bfinal versus indexed_final baseline result was received after design;
it did not change the128 grid or old-only weights.

Eight-cell cyclic rotations give each cell each dispatch position exactly once
within each task, twice overall. Four concurrent requests can finish in a
different order; planned order and actual timestamps are retained. This is an
exploratory source-context comparison, four groups per task; repeats and cells
are nested observations and neither task is a new independent test set.

Only existing old child checkpoint0128 is loaded:
`/project/alex_phd/runs/rlm-research-r4/sidecars/trec-leaf-sft-v1/outputs/attempt-001/checkpoint-0128`.
Adapter SHA256 is
`c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3`,
configuration SHA256 is
`ec773bc3b9de58af98a7c4dce9a40af795a4d05cd47284dbbfb27eac99b74174`.
Base Qwen3-4B-Instruct-2507 revision is
`cdbee75f17c01a7cc42f958dc650907174af0554`, manifest SHA256
`19619b44b0bd30bf5debe0960e6dfd6acc5be8287c581727456aa5d17699c18f`.

## CPU evidence

Focused TDD first produced six failures because study.py was absent and two
failures because owned.py was absent. Implemented source then passed all eight
focused tests in1.07seconds; the frozen preparation reran and recorded them in
CPU_TESTS.json. Coverage includes source/order/ID preservation, complete128
grid and counterbalance, no gold leakage, paired request equality, strict tags,
duplicate keys, cardinality, extra properties, invalid labels, unavailable
semantic alignment, null unrun scores, the real collector with eight synthetic
HTTP responses and preserved raw wire bodies, and single-adapter binding and
inclusive cleanup-budget boundaries. No broad test suite ran.

Exact command:

```
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q -p no:cacheprovider /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-anchor-padding-control-v1/test_study.py /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-anchor-padding-control-v1/test_owned.py
```

Native qualification compiled eight unique schemas, rendered128 typed-template
prompts and verified64 free/exact physical-prompt identity pairs. Maximum prompt
length is2832 tokens;2832+3072=5904, below8192 for every request. The inherited
physical renderer uses vLLM typed tool.model_dump ordering and does not mutate
the frozen requests. A further direct native xgrammar boundary check accepted a
synthetic valid64 result and rejected the corresponding63-record result for
every one of the eight task/representation schemas.

Tags q0000 through q0064 each tokenize to five tokens. Across every canonical
TREC/SST label, meaningful/placeholder synthetic outputs differ by zero tokens
under both compact and standard JSON. Their64-object output lengths range
771–963 compact or1026–1218 standard tokens depending on the label. This audit
fixes tags before inference and is not a claim of equal realized compute.
Placeholder instructions add exactly26 physical prompt tokens versus meaningful
instructions in every context. This wording difference, actual label mixtures,
serialization and free-generation behavior remain possible differences.

Final read-only owned verification exited0 and reported qualified source closure
verified and the single c32de adapter binding:

```
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-anchor-padding-control-v1/owned.py --verify
```

Native environment used Python3.12.12, torch2.13.0+cu130 with CUDA build13.0,
vLLM0.28.0, transformers5.6.2, httpx0.28.1, xgrammar0.2.1 and pyarrow24.0.0.
Available uv is0.9.7. The existing environment was reused unchanged; no new lock
was generated. CPU qualification emitted upstream torch deprecation warnings
and the expected no-visible-CUDA-runtime message, then exited0.

## Owned integration and proposed exact argv

No new scheduler or material lifecycle interface was needed. The helper named
dual-LoRA actually iterates binding.models and accepts one old alias; root and
children both refer to that single alias. It writes endpoint-original.json,
which its unchanged preflight and this collector consume. The owned wrapper
imports the suite privately and calls its authenticated start, command and
release helpers. The suite.py pin is
`6fa84af486efbf5bad17352553d36cd590fb6f7e386c2273df27dd8deb7c8fd1`,
manifest pin `4f37ffa367c6e50f27034060543caf93680d5239f2d5a09fe56cb817ab84f642`.
All128 requests use `strict-rlm-qwen3-4b-role-sft-selected-v1`; live model cards,
descriptor and version must authenticate before collection. No new binding
changes the request bodies at launch.

Main may integrate this exact argv after assigning one exclusively reserved GPU
and inheriting STRICT_RLM_CALIBRATION_API_KEY; PYTHONDONTWRITEBYTECODE=1 is advised:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-anchor-padding-control-v1/owned.py --directory /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-anchor-padding-control-v1/owned/attempt-001
```

The inclusive owned envelope is1800seconds from main entry, work deadline1680,
with120seconds reserved for authenticated cleanup. Collection has900seconds,
four concurrent HTTP calls,120-second configured HTTP timeout, zero retries,
temperature0.5/full support,3072 output-token cap and8192 context. Caps are
limits, not promised completion times. No training or checkpoints are needed.
The wrapper refuses an existing owned directory or collector attempt. It
releases only the service it owns via the qualified lifecycle.

Owned artifacts will be in `owned/attempt-001`; raw per-call requests/responses,
wire bodies, token IDs when available, usage including absent cache fields,
stop reasons, timing, output failures, model identity, hashes, analysis and
unrun accounting will be in `outputs/attempt-001`. Infrastructure/unrun outcomes
stay null. Malformed/tag/cardinality/ID errors are output failures with
unavailable semantic alignment and zero strict correct assignments, not64
established semantic label errors. Exact offline aggregate label counts,
position accuracy and confusion use fully aligned canonical outputs only.

Actual native service/HTTP integration remains unexercised by design. Main owns
launch ordering and automatic handoff. No blocking design question remains;
the readiness qualification is CPU-only, and current output-length neutrality
is synthetic rather than a realized-compute claim.
