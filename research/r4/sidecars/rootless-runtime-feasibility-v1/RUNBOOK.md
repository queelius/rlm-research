# Rootless Verifiers runtime and Prime/OOLONG handoff

## Decision

This machine can satisfy current Verifiers `RLMHarness.NEEDS_CONTAINER` without root. The staged
runtime is a deliberately narrow Docker-CLI adapter backed by rootless Podman, crun, a single
host-ID mapping, local VFS storage, and a digest-pinned image. Generated RLM Python executes in
the container, not in the host process. Current Verifiers lifecycle tests and one exact benign
RLM ACP turn pass through this boundary.

This is vetted only for the trusted exploratory OOLONG setup, whose task policy explicitly allows
all network access. The container shares the host network namespace. It is **not** a general
hostile-code production sandbox, and restricted-network mode is unsupported. All in-container
UIDs collapse to one host UID, so Unix account separation inside the container is also absent.
Do not use this wrapper for MRCR or the repository's host-executor RLM jobs.

## Pinned boundary

`PROVENANCE.json` records the Canonical-signed packages, exact deb hashes, commits, model and
dataset revisions, working-file hashes, and base/derived image digests. `MANIFEST.json` binds all
authored sidecar files. Runtime state lives only at `/tmp/rootless-runtime-feasibility-v1`; it can
be recreated after a reboot from the staged package cache at
`/project/alex_phd/cache/rootless-runtime-feasibility-v1`.

The Prime experiment reuses the 24 immutable OOLONG rows and exact official scoring port from
`official-rlm-prime-pilot-v1`: 16 train rows from context window 8 and eight held-out rows from
disjoint context window 6. It uses the local, commit-pinned Qwen3-4B-Instruct-2507 snapshot.

## CPU verification

```bash
root=/project/alex_phd/runs/rlm-research-r4/sidecars/rootless-runtime-feasibility-v1

"$root/tests/test_crun_wrapper.sh"
"$root/tests/test_docker_wrapper.sh"
"$root/tests/test_isolation_contract.sh"
"$root/tests/test_rlm_base_image.sh"
PATH="$root/bin:$PATH" \
  /project/alex_phd/envs/prime-rl-5990b1b/bin/pytest -q \
  "$root/tests/test_verifiers_runtime.py"
/project/alex_phd/envs/prime-rl-5990b1b/bin/python \
  "$root/scripts/seal_manifest.py" --verify
CUDA_VISIBLE_DEVICES='' "$root/bin/launch-prime-rlm" smoke --dry-run
```

The slower exact integration probes are `probes/verify_rlm_setup.py`,
`probes/verify_ipython_repl.py`, and `probes/verify_rlm_turn.py`. They require the same `PATH`
prefix and pinned Prime Python. Recorded results are under `artifacts/`.

## Two-GPU Prime systems smoke

Only launch after the current GPU owner releases both devices and localhost ports 8810, 8820,
8821, 8910, and 5555. The launcher checks source and manifest hashes, image identity, stale
containers, ports, and output overwrite before invoking Prime.

```bash
root=/project/alex_phd/runs/rlm-research-r4/sidecars/rootless-runtime-feasibility-v1
CUDA_VISIBLE_DEVICES=0,1 "$root/bin/launch-prime-rlm" smoke
```

Prime maps the first visible GPU to the vLLM inference worker and the second to the LoRA trainer.
The `rl` parent coordinates those workers and environment servers; each active RLM episode gets a
short-lived rootless container through the wrapper. The four-step smoke checkpoints every step
and evaluates the exact eight held-out rows before training and at step 4. Expect roughly 20–60
minutes. Resume the same run after interruption with:

```bash
CUDA_VISIBLE_DEVICES=0,1 "$root/bin/launch-prime-rlm" smoke --resume
```

Run the 25-step arm only after smoke proves: both evaluations complete, at least one training
group has unequal reward, checkpoints and LoRA broadcasts advance, and there is no systematic
container/setup/OOM/NaN failure:

```bash
CUDA_VISIBLE_DEVICES=0,1 "$root/bin/launch-prime-rlm" explore
```

Stop the exploratory arm if task errors exceed 10%, every reward group has zero advantage through
step 5, or trainer/inference weight versions stop advancing. It checkpoints every five steps and
is expected to take about 1.5–4 hours.

## Cleanup and interpretation

List only this adapter's isolated containers with `bin/docker ps -a`. Remove an exact stale
container with `bin/docker rm --force NAME`; never delete the shared cache or broad `/tmp` paths.
The wrapper refuses non-resume output overwrite and destructive Prime `--clean`.

Report held-out reward before/after, all task outcomes, reward variance, errors/truncations,
Python/RLM calls, tokens, wall time, checkpoints, and broadcast versions. A four-step smoke is
only a systems/learning-path result, not evidence of generalization.
