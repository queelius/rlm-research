# Native recursive action capture

Prepared September 8, 2026. Three explicitly reused development questions (12000008, 12000009, 12000025), executable-example prompt only, four fresh seeds each (950260900–950260911), temperature 0.5. Existing prompt/environment, native Qwen3 prefill, all-call exact causal capture, 30-minute cap, checkpoint after every episode. No heldout outcomes read and no further optimizer update authorized by this collection.

The supplied endpoint is the current one-update RLVR checkpoint, alias `strict-rlm-qwen3-4b-rlvr-final`. The immutable spec binds its descriptor, model/adapter/config hashes and an append-safe prefix of its **current** serving log, establishing processed sampler logprobs without copying credential-bearing log/config text.

## Launch requirements

The parent owns the server and sole GPU. This wrapper deliberately reuses the existing runner, but its frozen version omits the original launcher's PATH/cache setup. Both variables below are therefore required. Attempt 001 was preserved after ten infrastructure failures in 0.153 seconds: Docker was not discoverable, and no model calls occurred. Do not resume those failures as if they were policy samples.

```sh
PATH=/project/alex_phd/runs/rlm-research-r4/sidecars/rootless-runtime-feasibility-v1/bin:$PATH \
VERIFIERS_CACHE_DIR=/project/alex_phd/cache/verifiers-prime \
/project/alex_phd/envs/prime-rl-5990b1b/bin/python -B \
  /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-train-capture-v1/driver.py \
  --endpoint-descriptor /project/alex_phd/runs/rlm-research-r4/operations/2026-09-08-resume/inference-rlvr-tis-attempt-001/endpoint.json \
  --output-dir /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-train-capture-v1/outputs/attempt-002
```

`STRICT_RLM_CALIBRATION_API_KEY` must already be supplied by the parent. Never print or persist its value in research artifacts.

Once all twelve episodes finish:

```sh
/project/alex_phd/envs/prime-rl-5990b1b/bin/python -B \
  /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-train-capture-v1/export.py \
  --attempt /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-train-capture-v1/outputs/attempt-002 \
  --output /project/alex_phd/runs/rlm-research-r4/sidecars/recursive-train-capture-v1/exports/attempt-002
```

The exporter reuses the unchanged official-branch exporter with a process-local current-log binding. All sampled parent and child actions receive terminal episode credit; that is not independently verified child-label supervision. Completed malformed actions with complete capture can retain reward zero; infrastructure/capture failures have reward null. No group means no next update. Inspect mixed groups and semantic quality before deciding any further training.

## Verification and seals

Two new bounded CPU tests and two existing causal-branch/capture tests passed. A separate CPU fixture verified that semantic parent→child edges never get concatenated into a child's physical causal prefix. Current-spec preflight and exact prompt/environment equality against the self-SFT example spec passed; all twelve seeds are disjoint from its earlier sampler seeds. The actual Docker launch boundary was subsequently checked: absent before PATH correction, frozen wrapper resolved after it, version probe exited 0 (4.9.3). These CPU checks are not evidence of successful recursive GPU capture.

- SPEC: `e5f1a678b99b8f45a5c295a6d8f5a6a8806afac6bd770468d77510b6e203e040`
- Plan: `2dbdc44dbf7c9aa5d5ea2601a1eac7e33a9cb178653627362ecec1dbff5e905a`
- Driver: `763bf1223f3d54098efb5013555821ebbede3c347d9b846fa51ac1fd9b5354b6`
- Exporter wrapper: `3535e6aadd78d0a092df5ad0d1af3c38a288f63ab52552bc2f65b1ff6aed7043`
- Current server evidence: `8b54b0f998ecb0b72f6ccb176768883705fdeb786aa2c8546f6b8a14c9b0c820`
- Tests: `880385f8ea4eaa73b92c8cf196cf57e83fd6dd65bcd298c6fbaa584de835a1f5`

Failed attempt 001 has an explicit partial diagnostic export at `exports/infrastructure-attempt-001`: ten records, zero trainable episodes/actions, no group. Its sources and outputs remain unchanged.
