# Runtime install/cache feasibility — read-only finding

2026-09-09, inspected approximately 09:35–09:41 UTC. No installation, image creation, cache mutation, cleanup, container exec, GPU/model call or process signal was performed. This is a source-derived diagnosis and optional future intervention, not authorization to change any accepted job.

## Decision

The lxml setup null is explained at the installation boundary: each fresh episode container can perform an online, incompletely pinned Python dependency resolution. The harness pins nano source but not the installer uv release or the resolved tool environment. Neither the RLM installation nor its uv cache is mounted from the host cache. Warming `/project/alex_phd/cache/uv-prime` would therefore not address this path.

Prefer one future, independently named, digest-pinned **preinstalled runtime image**, built and CPU-qualified outside all live state. Reuse unchanged harness setup: its `.ready`/executable check should bypass the online RLM installer. First prove that bypass and qualify the separate ACP/script environments too. Do not retrofit this image into current BROAD or accepted successor jobs. A full dependency-lock installer is a stronger later intervention, but changes more than the minimal availability test.

## What failed, and what is not established

The sealed `analyses/root-broad-equality-continuation-live-2026-09-09/STEP12_INSTALLER_NULL_EVIDENCE.json` (SHA256 `e255e9e4e8b3c7dbf9911bbc75f3029b9b0cdd179fad51e8df0a0a0e5968bfc4`) records round09 episode `9657f9ca8f0c7f31495a2f99dbf1888605cacaa57f9e3ce942999948c71ebb38`: 137.69921875 s episode wall, zero model calls, HarnessError during setup. The preserved stderr tail identifies a metadata-fetch timeout after installer retries taking 126.1 s, for:

`lxml-6.1.3-cp311-cp311-manylinux_2_26_x86_64.manylinux_2_28_x86_64.whl.metadata`

This is not a model semantic error. The evidence does not retain the full shell request, failed uv version, resolved dependency closure, or network telemetry sufficient to distinguish remote service trouble, routing, bandwidth or local contention. The installation command below is reconstructed from source, not asserted to be a separately recorded runtime request. No reproduction/retry was attempted. Do not assume every setup null has this cause.

## Exact installation seam

Executed Prime file: `/project/alex_phd/research-cache/repos/prime-rl/deps/verifiers/verifiers/v1/harnesses/rlm/harness.py`, SHA256 `7256f1efe1d0b44c8488e62edc93c41fa2da1fae95620bc6de4dea2e7d517bfc`.

`RLMHarness.setup` uploads skills, computes `sha256(config.version)`, and invokes `runtime.run(['sh','-c',guarded], env)`. For the literal version string `4ef3438`, the directory is:

`/tmp/vf-rlm-4fa91253816bfa64435b7b727ec01bac2a7a7a2b72ece29ceb2474d26f95418d`

The guard is `mkdir -p <directory> && flock <directory>/install.lock sh -c <ensure>`. Ensure succeeds without installation only if `<directory>/.ready` exists and `<directory>/bin/rlm` is executable. Otherwise it removes the marker/checkout, ensures git, clones `https://github.com/PrimeIntellect-ai/nano-rlm.git`, checks out `4ef3438`, executes checkout/install.sh with UV_INSTALL_DIR and UV_TOOL_BIN_DIR both set to `<directory>/bin`, and creates `.ready` only after success. The complete reconstructed shell argv, including destructive operations inside its owned runtime directory, is retained in the cited STEP12 evidence; none was executed here.

The harness also appends `--with mcp~=1.28` to RLM_EXTRA_UV_ARGS. It does **not** set UV_CACHE_DIR or UV_TOOL_DIR. The exact final installer operation is:

```sh
uv tool install --python "$(select_tool_python)" --editable "$RLM_CHECKOUT" $SKILL_ARGS $EXTRA_UV_ARGS
```

For the observed no-packaged-skill case, source and tool receipt resolve its meaningful arguments to:

```text
uv tool install --python /usr/local/bin/python3 --editable /tmp/vf-rlm-4fa91253816bfa64435b7b727ec01bac2a7a7a2b72ece29ceb2474d26f95418d/checkout --with mcp~=1.28
```

The pinned install.sh unconditionally downloads `https://astral.sh/uv/install.sh` and installs latest uv, even if the image already has uv. It also checks curl/CA/ripgrep and may perform system-package operations. Its pyproject directly lists unpinned `lxml`, plus many other unpinned/ranged packages (numpy, pandas, scipy, ipykernel, openai, pydantic, etc.); agent-client-protocol is pinned to 0.12.1. `install.lock` is only an OS flock coordination file. `.ready` is a successful-install sentinel, not a dependency manifest. Its key includes only the version string, not Python, uv, extras, skills or environment hashes.

### Concrete commit versus lock evidence

Read-only `/proc/<pid>/root` inspection of an already-live runtime at 09:39:27 UTC found detached checkout HEAD `4ef3438d55fdd39b18d34035833c73e13b006733`. The full installer was read, not inferred from the unrelated later nano clone in the external repository cache (that clone did not contain this revision).

| Live checkout file | SHA256 |
| --- | --- |
| install.sh | `bdd5d2d2864785e8511d0ae59ae984c75391a86fef6bc04cd194e24c644d92f3` |
| pyproject.toml | `e9d680f50a32241e5f7144d8dd12cef2b9e8ba4082f6b6a9dfb69519442f56d7` |
| uv.lock | `6ce7d3c153d9ddc979de5f9d44966cb7f2209f40e32619b304a525579eda59d1` |

The repository uv.lock exists and lists **lxml 6.1.1**, while the failed setup requested **6.1.3** metadata. The installer does not use `uv sync --locked/--frozen` or consume an exported hash-pinned dependency set; it invokes `uv tool install --editable` instead. Thus presence of a repository lockfile is not evidence that this installed environment followed it. The live tool receipt lists editable rlm plus `mcp~=1.28`, not the complete resolved transitive package graph. Its pyvenv.cfg records **uv 0.12.11, CPython 3.11.16**. These are observations of a successful contemporaneous runtime, not a reconstruction of the failed runtime's versions.

## Cache lifetime, actual mounts, and ownership

Pinned DockerRuntime start source (`deps/verifiers/verifiers/v1/runtimes/docker/__init__.py`, SHA256 `2bac5b2404f5177f8fb603f91ae9b6509290f117b5633f7404ff1473b36979ce`) creates a new named container per runtime. It does not bind a host uv/install cache. The pinned compatibility wrapper `sidecars/rootless-runtime-feasibility-v1/bin/docker` (SHA256 `daab60dcd7bf6c9f0c49f77b39ab5883776bd4ccc93eed596819efe17460f36b`) adds only `/app` tmpfs to these ordinary run invocations and uses rootless Podman/VFS storage.

An actual live OCI config was read at `/tmp/rootless-runtime-feasibility-v1/root/vfs-containers/7c7990910363b170e40b671c61d41119e70592d6443f258998887cc0bcf5f1ce/userdata/config.json`. It showed `/app` tmpfs and ordinary proc/dev/sys/hostname/resolver mounts, with **no `/tmp/vf-rlm`, `/root/.cache/uv`, or host research-cache bind mount**. HOME was `/root`; UV_CACHE_DIR and UV_TOOL_DIR were absent from the selected environment fields. The actual running CLI used `/root/.local/share/uv/tools/rlm/bin/python`. Another live runtime confirmed `/root/.cache/uv` exists. These are per-container filesystem locations, not host `/project/alex_phd/cache/uv-prime` or `VERIFIERS_CACHE_DIR`.

The source-version directory, `.ready`, uv download cache and tool venv can be reused **within that same container**, but newly completed installs do not populate a common cache for subsequent fresh containers. New containers can inherit only whatever their base image already contains. The current frozen scientific image ID is `sha256:53a70288e91a75c9bc8cbc9a75da4c3d156227266fd8c6c997deb8ef7f921552`, with tag `localhost/verifiers-rlm-python:3.11-slim-single-id-v1`. The source builder `bin/build-rlm-image` (SHA256 `c55f2e865818ca45b66be92fb38a5fe146e4d08db4f330fe3a730c4351e5ea96`) provisions git on pinned Python-base ancestry; it does not preinstall nano. Its early tag-exists return is another reason not to reuse it as a mutable “refresh” mechanism for this proposed change. No current image layers were edited or exhaustively re-audited.

Owner checks: `/tmp/rootless-runtime-feasibility-v1`, its root storage, `/project/alex_phd/cache/verifiers-prime` and `/project/alex_phd/cache/uv-prime` belong to atowell, UID 1523821556. Live runtime PID 3436092/start ticks 1075054607 had uid_map `0 1523821556 1`; namespace root maps to that single host user. Existing Podman process PID 1047384/start 1069900783 belongs to the rootless feasibility runtime, and multiple conmon/ACP processes were live during inspection. Merely sharing a UID does not establish task ownership or permit mutation. The sampled container/PIDs disappeared naturally during read-only checks; absence was not treated as permission to clean anything. All shared state remains owned and untouched.

The wrapper's persistent host storage is `/tmp/rootless-runtime-feasibility-v1/{root,runroot,runtime,tmp,home}`; staged executable packages are under `/project/alex_phd/cache/rootless-runtime-feasibility-v1/rootfs`. These are live shared infrastructure, **not free preparation targets**. Host-only Verifiers caching and model/uv training caches are separate concerns.

## Smallest future qualification, with limits

Three options differ materially:

1. **Host cache prewarming alone: reject.** The target caches are not mounted, and install.sh still downloads latest uv. Adding a shared writable cache mount would be a new runtime/safety/provenance contract, create concurrent mutable state, and still not pin resolution.
2. **Fresh preinstalled image: preferred narrow availability experiment.** In a new task-owned builder namespace and new image tag, based on the exact current digest, run the unchanged harness installation once with the exact version string, empty packaged skills and `--with mcp~=1.28`. Preserve the version-keyed checkout, tool venv, shim, `.ready`, and required uv/script environments in the image. This freezes the installed result by image digest; it does not retroactively make the original online resolution locked. No broad host cache sharing is needed. Keep original runtime image/source unchanged and parent-approve a separate future run.
3. **Explicit locked installer: stronger but larger follow-up.** Replace latest-uv/bootstrap and tool resolution only in a new qualified image build with a pinned uv binary plus a recorded, hash-checked dependency artifact set including injected MCP and build dependencies. The existing project uv.lock alone is not sufficient evidence of parity; adopting its lxml 6.1.1 would itself change the environment relative to recent installs. This should be treated as a declared environment intervention, not hidden repair.

For option 2, no new model calls are needed initially. Proposed bound: one clean build attempt, at most 900 s/2 CPU workers, then two fresh child containers from the immutable resulting digest, at most 180 s each, running existing harmless native ACP/fake-broker fixtures and the exact installed overlay. Record every failure, with no implicit repeated builds. Verify exact nano engine/client source hashes, interface behavior, runtime ancestry and physical request identity against the existing CPU contract. Observe full setup/install command traces, start/end times and outbound installer attempts. The second fresh-container setup must demonstrably pass the original `.ready` guard without git/uv/PyPI fetches; use network-denied installation qualification or trustworthy scoped capture, not only a short elapsed time. Do not freeze a success sentinel manually or put a nonexistent shim behind it.

Important residual: Prime `runtimes/base.py` SHA256 `c7f8635076529ac81483c79a06a4e01b6fa46ac676f8924b817231d40f84dead` separately prepares PEP723 scripts via `uv sync --script <content-hash>.py -q --no-config` and `uv python find --script ...`. Its interpreter lookup cache is runtime-local. Prewarming only the nano tool therefore does **not** establish fully offline ACP setup. The minimal qualification must exercise the exact full native fixture and retain the necessary script/cache environments in the image or explicitly report any remaining online resolution. Do not build a general-purpose cache framework if this narrow proof fails.

Before any future model comparison, publish build source/command logs, base and new image digests, exact nano commit and working-file hashes, Python/uv binary versions and hashes, resolved installed package versions plus wheel/source/build-artifact hashes, inherited project uv.lock hash with its actual usage stated, injected extras/skills, image layer or archive manifest and owner namespace. Do not claim a receipt listing only top-level requirements is a full dependency lock. Resolve builder storage/disk ownership before launch; a new tag alone does not isolate the currently shared Podman storage.

## Research implication

This boundary can add setup latency, consume the same allocation without model work, and produce task-null exclusions independent of answer correctness. Online dependency drift also weakens exact runtime reproducibility across dates/episodes despite fixed nano commit and base image. The current evidence proves a specific installation timeout and an unlocked resolution seam, not measured cross-episode package drift or altered learning behavior. Keep these nulls separate from wrong answers and include setup costs. No source-derived cache remedy rescues the missing episode or authorizes rerolling its reward. Promote only the smallest future intervention that passes the isolated CPU qualification; leave current accepted runs untouched.
