# Parent-owned launch

Use the qualified Prime interpreter, not a CPU environment lacking the inherited Verifiers imports. This driver neither creates a service nor owns its lifetime. Parent supplies the actual live old-c32de descriptor; a historical descriptor is not proof of a live service. Binding authenticates the adapter/config/base files without contacting the endpoint. Run independently checks live version and alias/root/base before any completion request.

From this sidecar directory, with the service API-key environment already supplied by its owner:

```bash
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python driver.py verify
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python driver.py bind --endpoint-descriptor /ABSOLUTE/ACTUAL/endpoint-old.json --spec-path BOUND-attempt-001.json
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python driver.py run --spec-path BOUND-attempt-001.json --output-dir outputs/attempt-001
```

Root: `/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-correspondence-anchor-transfer-v1`. Use absolute paths if launched from elsewhere. The descriptor must identify adapter c32de1293c01bba5104eb1f123867649c71dd38e5194661ace4b17dcbbe66ba3 at the original selected checkpoint, with its matching config; no generic adapter substitution is accepted. Credentials never enter artifacts.

The live job has 600 maximum completion calls, four concurrent workers, common3072 output cap, per-call120s timeout and hard1800s collection wall cap including live preflight. Batch64 stress is dispatched first; competence5 uses permutation0 only. No retries or resume into existing output. Every bound spec/output path must be new. If interrupted, inspect immutable calls/wire records and STATUS; do not invent results for unrun cases. Any repeat is a separately recorded new attempt with an explicit relation to the old attempt, not an automatic retry.

Inspect STATUS.json first, then analysis.json and raw calls. Typed physical prompt matches must equal recorded responses before claiming identical intended inputs. Physical token IDs and all raw response usage are retained; reported cache counts are not inferred. Malformed cardinality/IDs remain invalid/unaligned, and infrastructure failures remain distinct. Compare paired contexts and stable source IDs, not600 independent observations; report exposed TREC and new SST task-transfer separately.

CPU qualification compiles every distinct ordered schema, renders all600 requests through the actual typed vLLM tool serialization, verifies prompt+3072≤8192, and exercises two fake native first-leaf responses via the inherited collector. It does not execute generated tools or perform a real model/GPU call. READY.json is the sole completed-preparation marker.
