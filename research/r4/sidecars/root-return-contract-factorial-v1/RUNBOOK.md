# Parent launch only

Preparation uses `/project/alex_phd/envs/prime-rl-5990b1b/bin/python` with
`CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1`. No server or GPU was used to prepare.
The fake-provider qualification creates only uniquely named owned rootless CPU runtimes.

After the main coordinator has read and accepted the new source, and the previous GPU owner
has released the device, supply exactly one assigned `CUDA_VISIBLE_DEVICES` and the existing
`STRICT_RLM_CALIBRATION_API_KEY` environment variable. Do not print either credential or inference config.
Then run from any directory:

```bash
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-return-contract-factorial-v1/driver.py verify
PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-return-contract-factorial-v1/driver.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-return-contract-factorial-v1/outputs/attempt-001
```

The runner does not attach to the previous service. It authenticates exact root/child/config
bytes and launches the unchanged `leaf-role-routing-v1/source/serve.py` on its qualified ports
18601/18611/18621; occupied ports fail closed. It then authenticates actual descriptors and live
`/models` alias/path/parent cards before any model request. Two weight phases run serially;
each contains the same task/seed pairs, balanced instruction order, eight pair workers.

The global 3600-second clock starts before service creation. Per-phase capture is at most
1800 seconds and retains the original episode budgets. Ninety seconds is reserved for final
collection/runtime/service cleanup. The unchanged lifecycle V2 stops only authenticated owned
PID/start/uid/group identities and observed descendants, checks they are gone (not only closed
ports), and records release. A release failure is a stop requiring main diagnosis; never start
another GPU job on the assumption that closed ports prove release.

Outputs are immutable per episode. `TERMINAL.json` distinguishes operational failure/cap from
completion. Per-phase `rollout/STATUS.json`, `episodes/`, and `rollout-routing/role-audit/` retain
attempts and physical IDs. `ANALYSIS.json` contains task/seed paired contrasts and six context
clusters, not an independent96-episode test; missing outcomes remain null. If post-release CPU
analysis fails, its error is separate from GPU collection and the immutable raw data remain.

No resume or retry is exposed: an interrupted/capped study is evidence, not permission for extra
samples. There is no adapter update, reward change, response repair or generic service cleanup.
