# Allocation5780 runtime restoration

Update after first actual launch: original attempt001 is now a retained pre-model credential failure; do not use the initial command below again. The final section documents the separately prepared fresh recovery entrypoint and unused attempt002 output. CPU/runtime proofs remain valid.

Ready for MAIN's separately accepted parent. Final executable is:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/runtime-an27-5780-v1/study_wrapper_v3.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-complete-demonstration-sft-v1/outputs/attempt-001
```

The parent must retain affinity containing CPUs14,15 and its actual assigned GPU/deadline. Runtime processes pin themselves to14,15. MAIN owns GPU admission, credentials, parent acceptance and launch. This task launched no GPU process, touched no coordinator locks, changed no original scientific source/READY, mutated no environment, and deleted no files.

## Exact acceptance identities

All runtime paths below share `/project/alex_phd/runs/rlm-research-r4/sidecars/runtime-an27-5780-v1/`.

| Artifact | SHA256 |
|---|---|
| CPU_READY.json | 4ed1d5959738c46e06974f6dc63ba768ea2543f7fee8b4f6e1274e208c97c844 |
| LIFECYCLE_READY_V2.json, final launch amendment | 566407d55734dd0b0f06e387ea0352ad7e1275988a8dc5c1617d95d48ab88abb |
| study_wrapper_v3.py, final entry | 4f4e0281b01b319bcaf83b2fedff40d7ebb39419d4ad329ab9d88841ad1adeb2 |
| service_wrapper_v2.py, actual service entry | d7518bdca023fdfe112a0ee11cb094b95ab2ce551a29ecacfca9c2b9f18ea1fd |
| lifecycle_adapter.py | 18a5f3cc5003f294422c170826ac1595bd379f9958d52b00b59339ea24927375 |
| bin/docker | ac6b1f20f6e58aeb3e8311b419ca31088daf9aab5d89775ef885ed9e5033e7e3 |
| Original complete-SFT READY.json, unchanged | c9fc31943e81f8b3597e134a5e26b6d9c162e868356d20a37765081fca4b5b23 |

CPU_READY and final lifecycle manifest contain the complete source/artifact hash closures. Earlier study_wrapper.py/v2 and LIFECYCLE_READY.json remain as preserved construction stages, not final launch entries. No service was launched with them. MAIN caught the original-path ownership mismatch during review; v3 fixes it symmetrically before launch.

## Lifecycle-only differences

| Seam | Old | New |
|---|---|---|
| Node/UID | Historical an21 cache | an27, UID1523821556, owned allocation5780 metadata |
| Ephemeral VFS store | Missing /tmp/rlmc.0m4242 | mktemp-owned /tmp/rlmc.an27-5780.jL5eG5, mode0700 |
| Runtime affinity | 34,35 | 14,15 within observed0..15 |
| Runtime/cache root | runtime-local-cache-v1 and old /tmp | runtime-an27-5780-v1 wrapper and deterministic per-output caches beneath owned new /tmp |
| Driver environment | Helper forcibly prepended old580.126.09 compatibility library/bin | After helper computation, remove old library entries, prepend actual /export/software/system/nvidia/580.159.04/lib and replace old nvidia bin |
| Collector subprocess invocation | Original capture.py/readout.py directly | Accepted study_wrapper_v3.py dispatches the same original source with rebinding in each process |
| Native interface installation | Original st.local.LOCAL/STORE and validate_store/delta | Same original configure_interface function using new LOCAL/STORE, owner/image validation and explicit new delta |
| Service invocation | Original serve.py | service_wrapper_v2.py executes pinned original service with one counted environment seam and actual wrapper __file__ identity |
| Initial/release ownership | claim_service hard-coded original service path twice | Exactly two counted substitutions bind actual wrapper argv/hash; both initial claim and release use the same function |

The original binding.py remains exact: same low66c root and c32 child identity. Original study ROOT and attempt location, launch budgets, training subprocess argv, fresh-Adam recipe, loss masks/coefficient, checkpoint policy, capture/readout coordinates, prompts, parser behavior, service config and process ownership checks remain those of the pinned science sources. PID/start/UID/PGID, request/start/binding authentication and worker cleanup have not been relaxed. The service records ALLOCATION_DRIVER.json, the study ALLOCATION_RUNTIME.json and each native example LOCAL_RUNTIME.json.

## Immutable cache reconstruction

Copy source: `/project/alex_phd/research-cache/runtime-images/rpi-v2.kCaOH4/root`.
Exact image: `8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c`.
Frozen six-layer metadata SHA: `84c0481f9779aafb0d736a75189f793322b28ad29e9a438be0b03e447764e721`.

The pinned prior bounded copier was reused with only affinity replaced. It copied the selected immutable image directory, six immutable layer directories and six tar-split files, then wrote private images/layers JSON derived from frozen metadata. No live Podman database was copied or altered. COPY_PLAN.json records all paths and caps; COPY_MANIFEST.json records62880 per-file source/destination hash or symlink mappings. Source apparent bytes1684878918; conservative two-source-plus2GiB estimate5517241484 within12GiB cap. Copy24.4617s; copy/hash39.5827s; private inspect verified exact image. Store apparent bytes after fixture cleanup1340783287.

Ownership checks reject changed node/UID, missing/symlinked or group/world-accessible store, and unavailable required CPUs. Podman uses private root/runroot/runtime/config/tmp with staged qualified binaries, unchanged no-new-privileges/cgroup/VFS behavior, and no HOME reassignment. Missing cache invalidates readiness; no automatic recopy, fallback or retry.

## Focused verification and actual fixture

Executed from the new sidecar with PYTHONDONTWRITEBYTECODE=1:

```text
/project/alex_phd/envs/rlm/bin/python -m unittest test_isolation -v
/project/alex_phd/envs/rlm/bin/python copy_image.py
/project/alex_phd/envs/prime-rl-5990b1b/bin/python fixture.py 3
/project/alex_phd/envs/rlm/bin/python seal.py
/project/alex_phd/envs/rlm/bin/python -m unittest test_service_wrapper -v
/project/alex_phd/envs/rlm/bin/python -m unittest test_lifecycle_adapter -v
/project/alex_phd/envs/prime-rl-5990b1b/bin/python study_wrapper_v3.py verify
```

Eleven focused tests passed: four isolation/negative ownership tests; two command-routing/local callback tests; two driver/one-source-seam tests; three actual launcher identity gate tests. The seal includes the six initial tests in TESTS.json; final lifecycle manifest records the additional five. All original scientific source/input hashes and both new source closures passed final v3 verify. A separate CPU import check confirmed the actual original complete-study stack points to the new local runtime and cache while preserving its exact scientific image.

Exactly one native fixture was run. Slot `fixture-03` is the inherited compatibility branch name, not three attempts on this node. Its result:

```json
{"real_owned_rootless_runtime":true,"real_TrainClient_and_native_renderer":true,"provider_calls":3,"credited_root_calls":2,"uncredited_child_calls":1,"exact_physical_prefix_and_wire_tokens_verified":true,"gpu_calls":0,"provider":"CPU deterministic fixture only","synthetic_logprobs_not_measurements":true}
```

All three root-child-root calls matched historical native physical tokens, sampling and aliases exactly; cache salt alone is intentionally excluded. Fixture23.5513s; offline setup1.60373s; zero remaining private containers. Fixture RESULT/COMPARISON/TIMING/SETUP_COMMANDS and all captured evidence remain under fixture-03. No failed fixture or rerun occurred. This is runtime transport evidence with fake provider, not GPU/training/model-quality evidence. The inherited installer denial canary is scoped installer evidence, not a general network sandbox.

## Limits and concerns

The12GiB proof cap covers copy plus one fixture and does not qualify arbitrary concurrency or cumulative future cache growth. The prepared workflow is serial; MAIN should observe its actual cache/memory growth. Tmpfs bytes count against the allocation's memory and remain until explicit owner-checked cleanup. No cleanup was performed. Driver adaptation and service identity gates passed CPU checks; their live model startup remains the experiment's initial exploratory service stage. Readiness does not imply model qualification, general speedup or scientific outcome.

The urgent target was exceeded because recursive service environment and launcher identity dependencies required two additional narrow lifecycle adaptations. The successful cache/fixture itself was ready promptly; the later checks prevented a known ownership failure from being launched. No GPU utilization claim is made for this CPU task.

## First actual launch failure and fresh recovery

MAIN's original complete-SFT attempt failed after4.94334s, before launching inference. Retained teacher-service/launcher.log gives the exact cause: `KeyError: 'STRICT_RLM_CALIBRATION_API_KEY'` at the pinned service's `key = os.environ[...]` lookup. The accepted parent had not supplied the local-provider credential. The helper driver transformation had completed; no SERVER_START, corpus or training directory was created. All48 readout coordinates remain unrecorded/NULL. The original TERMINAL, RUN, launcher log and immutable scientific sources are pinned in the recovery manifest. This was a parent-environment readiness omission, not evidence about model behavior or the SFT recipe.

Approved credential source supplied by MAIN: `/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-output-cue-order-v1/owned/attempt-001/service/inference.json`, `vllm.api_key`, exactly one nonempty string. MAIN privately binds it into `STRICT_RLM_CALIBRATION_API_KEY` in the parent environment. No credential value was printed, written into new artifacts, placed in argv, synthesized, or changed.

Added `credential_preflight.py` requires the inherited nonempty variable before any original verify/run dispatch. A narrow missing/empty/blank/valid regression passed; a mocked dispatch check confirmed missing credentials cannot reach original attempt creation. `study_wrapper_v4.py` is the standalone credential-only adapter, not the fresh recovery entrypoint.

The fresh recovery executable is:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/runtime-an27-5780-v1/recovery_wrapper.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-complete-demonstration-sft-v1/outputs/attempt-002-an27-credential-recovery
```

`RECOVERY_READY.json` SHA256 `c6e96918d6964b8d4eb53ffa1b6156277c437dbb7387f9d43465139302784be4`; `recovery_wrapper.py` SHA256 `91673f58d7e71313a1e5817cf421eab157c94688001b0b478423eb4435e848c5`. MAIN must accept this fresh attempt separately and bind the credential privately. This task did not launch it or create its output directory.

The recovery preserves `s.ROOT` and the complete original READY identity `974c38ad8d0fdbb59f734f7fc2fb8b07e8bb1ac825a868e645ff508ff14a9604`. It replaces only literal output namespace `outputs/attempt-001` with `outputs/attempt-002-an27-credential-recovery`: one occurrence each in study.py, binding.py, train.py, and two in launch.py. Three launch argv entries route capture/train/readout through the recovery wrapper; their original NATIVE/TRAIN interpreters, flags and caps remain exact. Each subprocess installs the same transformed study/binding, so corpus, training checkpoints and readout selections agree. Capture.py and readout.py source bytes are unchanged. Original scientific files are executed through counted in-memory transforms and remain unedited on disk. Exact original/transformed hashes and evidence membership are in RECOVERY_READY.

Both exact-source/output-diff and three-subprocess argv tests passed. A real CPU module composition check confirmed the scientific root remains original, both training bindings point to new attempt002, and the unchanged start binding remains original low66c. `recovery_wrapper.py verify` passed with the approved credential read privately: original scientific/source/input and runtime/lifecycle/recovery manifests all authenticated, zero GPU calls. The full native fixture was not repeated.

The new attempt is fresh Adam from the same original start because predecessor001 never reached a model call, captured example or optimizer update. It is not an optimizer resume and does not discard or reroll any scientific observation. Original seeds, masks, targets, coefficient, data, prompts and checkpoint policy are unchanged. No failed artifacts were overwritten, moved or removed.
