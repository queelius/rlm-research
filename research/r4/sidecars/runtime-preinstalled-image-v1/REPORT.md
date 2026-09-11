# CPU preinstalled-runtime attempt: stopped at CLI preflight

Status: **NOT READY; no image built; isolation feasibility remains untested.**

The first task-owned Podman invocation exited125 after0.031s with `Error: unknown flag: --signature-policy`. The new adapter incorrectly placed that option in the global argument list for `podman info`. This is an implementer CLI compatibility error, not a finding that external storage, single-ID rootless operation or preserving HOME cannot work.

The exact argv/stdout/stderr/scoped environment are preserved in ISOLATION.json; ATTEMPT.json records the single900s build allocation and two180s maximum fixture allocations. No second invocation, corrected retry, base export, private load, container, package install, image commit/retag, native fixture, GPU/model call, shared-store writable operation or process signal occurred. The failed option was parsed before Podman storage initialization. Only new empty owner directories and the new sidecar were created. They are preserved for a separately authorized continuation, not deleted.

New external storage: `/project/alex_phd/research-cache/runtime-images/rpi-v1.WHYd2G`, created by mktemp under the expressly authorized runtime-images root. Its named root/runroot/runtime/config/tmp directories were created mode0700. Owner UID1523821556. HOME was preserved exactly; XDG_RUNTIME_DIR/XDG_CONFIG_HOME/CONTAINERS_CONF/registries/TMPDIR and root/runroot point only to new task storage or new config. CPU affinity was32,33. Initial project filesystem free space was489332095844352bytes; no heavyweight allocation occurred.

Focused TDD: two desired adapter tests first failed because isolation.py did not exist; after implementation both passed in0.02s. They exercise private path/environment preservation and /app+CPU flag construction, but did not validate actual installed CLI support. The real bounded integration preflight exposed that missing compatibility coverage. Tests passing did not establish container isolation. Raw failing preflight is primary evidence; there is no CPU-ready claim.

Smallest explicit alternative, requiring a fresh parent decision because the current contract forbids hidden retries: remove the unsupported global flag and put the trust policy at the private XDG_CONFIG_HOME/containers/policy.json location, with all other writable state still private; first check installed CLI help/config semantics read-only, then perform one newly declared isolation attempt. Do not use this failure to justify invoking a shared live-store writer or copying the old HOME-reassigning wrapper. The current source is retained as failed-attempt evidence, not silently corrected.

Original53a702 image, nano4ef sources, all accepted jobs and all shared environments are unchanged. Successful-install .ready, resolved package/uv manifests, new image identity, full PEP723 offline proof and two native prompt/sampling/ancestry comparisons are **unavailable because execution never reached those stages**. No fabricated placeholder substitutes for these missing requirements.

The executing-plans/isolation/TDD skills structured this bounded attempt; the explicit no-retry decision and isolation failure caused work to stop. Main alone decides whether to authorize an additive corrected attempt.
