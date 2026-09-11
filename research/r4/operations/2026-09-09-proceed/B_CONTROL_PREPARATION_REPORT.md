# B80 control is CPU-prepared; parent acceptance is still required

The approved control adds Bfinal on the exact grammar160 requests. This prevents
mistaking broad mixed-size training for a benefit specific to indexed-output SFT:
the preceding matched free-HF readout was B373/384 versus indexed-final374/384.
No model requests, service starts, GPU work, queue changes or accepted160 edits
were performed in this preparation.

## Frozen inputs and implementation

Sidecar: `/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-grammar-B-control-v1`.
DESIGN.md, PLAN.md and README.md explain the question, interface and limitations.
SPEC.json contains eighty exact request templates and an explicit crosswalk to
both parent weights, referencing unchanged parent DATA.json. The old-weight
subsequence preserves the parent's relative counterbalanced dispatch order.
Only the model alias changes, including serialized key order and schema bytes.
No data loading/resampling, prompt reconstruction, repair or training was added.

The private helper imports reuse frozen grammar scoring, first-response HTTP
collection, raw-wire capture and native rendering. The owned wrapper reuses the
unchanged qualified suite/start_service and authenticated PID/start-ticks/UID
cleanup, including PRL::Inference handling. One B alias is sufficient;
`endpoint-original.json` is a historical filename for that truthful B descriptor,
not an assertion that it serves original weights. There is no endpoint-selected
dependency and no import of newly unfrozen padding code.

B's exact fixed-final epoch2/step204 model is
`59ad854293142161f6b5e613dd5d1e3630fed600637106d5eae2cbcd764e9200`.
WEIGHTS.json authenticates config, RESULT, SELECTION, source recipe/data identity,
checkpoint state and every saved Adam/RNG member. It is not validation-selected.

## Focused evidence

- Desired tests initially RED: all five failed because the companion did not exist.
- Final native CPU run: six tests PASS in1.03s. They cover80→160 exact crosswalks,
  alias-only serialized bodies, strict parser/missing alignment, real fake-HTTP
  wire/usage capture, no-retry provider400 as infrastructure null, deadline/weight
  rejection, and owned release after a failed collector.
- Four unique grammars compile. All80 native typed prompt hashes equal both parent
  counterparts. Full token arrays are retained in PROMPT_IDS.json. Maximum prompt
  length2799; plus3072 output cap=5871, below8192. Grammar and weight do not change
  physical inputs within representation; anonymous versus indexed contract text
  differs exactly as in the parent.
- `owned.py --verify` exits0 with GPUs hidden, authenticating unchanged lifecycle.
- CPU-only endpoint binding fixture additionally checks all80 bound requests
  change only the model alias. `cpu-binding-probe` is explicitly not a live service
  descriptor and must not be used for launch.
  An initial fixture invocation in default Python correctly stopped because that
  environment lacks vLLM; repeating in the prescribed native interpreter passed,
  without any network/model requests or source changes.

Qualified native stack: vLLM0.28.0, transformers5.6.2, httpx0.28.1,
xgrammar0.2.1, pyarrow24.0.0. Existing native Python only; no installs.

## Exact proposed parent invocation and clocks

READY.json is authoritative and supersedes the earlier illustrative README path:

```
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-grammar-B-control-v1/owned.py --operation-root /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-after-grammar-followups --directory /project/alex_phd/runs/rlm-research-r4/operations/2026-09-09-after-grammar-followups/B80-owned
```

Require parent PLAN/ACCEPTANCE with that exact argv and the actual inherited MIG
UUID/LD environment; do not replace CUDA_VISIBLE_DEVICES with0. Parent retains
launch ordering and GPU-empty checks. Wrapper verifies semantic weights and
source hashes before it starts the execution-stage clock.

Timing clarification made after SPEC froze, without changing frozen code:
900s collection, four workers,120s HTTP timeout, T0.5/full support,3072 output cap.
The wrapper's1800s covers execution-stage startup/collection/cleanup, with120s
reserved for cleanup. CPU source verification precedes that clock. Use1830s
parent total cap to include verification allowance; this is not a claim that the
inner1800s clock includes interpreter/preflight time. No retry, no filler, no
adaptive scheduler. Preserve partial/error/null outputs and release only owned
workers in finally. All operation/stage/collector markers remain available.

## Identities and interpretation

| Artifact | SHA256 |
| --- | --- |
| driver.py | ff03d7cd540ef41c9a2b7b6b6eec42a4025b7232d92f5b33610c64dce76748fa |
| owned.py | a4084e7419b48690fc6cb704682da7d2c3b22e8f308247ac4452d172d9619565 |
| test_control.py | 6f6b85aa228cef3c24543ca3ff6038b0ba84daefa76da3022705c2791f3cb3a6 |
| SPEC.json | 80c814648d896249cd15ef672a2b8d769f992f0ed5683a719f8d13f4e4676b02 |
| WEIGHTS.json | b7e6317802d9d6ad9c9e89028859e25e540099eebd84e191e930712fe47f3032 |

Prepared identity: `0f0e0e8fef0547dfcba058a984039b0748ae08daddaf4bc4da6fcbb9345dd026`.
READY carries the remaining source/input/qualification closure.

Compare B with indexed-final within task, representation and grammar, using
parent-coordinate pairing. Report strict whole64, validity, aligned semantic
accuracy, positional errors and actual tokens. Invalid structure is unavailable
alignment, not64 independently established wrong labels; provider errors and
unrun coordinates remain null. Six TREC contexts are exposed; four SST contexts
were fresh at the parent freeze, while public pretraining exposure is unknown.
This post-HF, later-service-stage addition is not a contemporaneously interleaved
three-weight replication. It can discriminate representation/training effects at
the component level, not demonstrate general RLM orchestration improvement.
