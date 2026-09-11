# Bounded preinstalled-runtime CPU decision

September9,2026. Main read the complete installer/cache feasibility report
ffd8e5612752b7445d0846b343fc0ab92c128f8a276ceaadab8c8088f41c87f7,
and the complete current image-builder48lines and Docker compatibility wrapper73lines.
This authorizes only a new isolated CPU preparation/proof, not a change to any
accepted GPU job, source, environment, image tag or live container.

Question: can a digest-pinned image containing one real successful native install
eliminate per-episode installer/network work without changing the intended RLM
source, native prompts or tool/ACP behavior? The observed lxml setup null and
unlocked tool resolution justify this narrow operational experiment. Host-cache
prewarming is rejected because current episode caches are container-private.

Implement under a new sidecar runtime-preinstalled-image-v1 and new task-owned
external image/builder storage under /project/alex_phd/research-cache/runtime-images.
Resolve and record ownership, unique paths and disk headroom first. Use explicit
separate Podman root/runroot/config/runtime directories; never reuse the live
/tmp/rootless-runtime-feasibility-v1 state as writable builder storage. Do not
repurpose HOME/home/CODEX_HOME in new scripts. Preserve existing source images,
configs, caches, tags and containers. Reading/exporting the exact immutable base
through a bounded read-only owner-defined image export is permitted; do not
commit/load/retag in shared live storage. If isolation cannot be established,
record that CPU feasibility limit and return rather than modifying shared state.

Base must be exact current image53a70288e91a75c9bc8cbc9a75da4c3d156227266fd8c6c997deb8ef7f921552.
Use exact nano4ef3438d55fdd39b18d34035833c73e13b006733 via its current guard/version
string4ef3438, same empty packaged skills and injected mcp~=1.28. Perform one real
successful installation; never fabricate .ready or a shim to bypass a failed
install. Preserve complete installed source and package/binary/version manifests.
Image digest freezes the resolved result; it is not proof that original online
resolution obeyed uv.lock. Do not silently replace the installer with lockfile
resolution, since that changes the declared environment intervention.

One bounded build attempt, at most900seconds and two CPU workers. Then at most
two fresh owned-container native CPU fixture checks, each180seconds. Capture
failed attempts and return without implicit rebuilds/retries. Ordinary inherited
installer retry behavior remains part of that one bounded attempt and is logged.
No GPU/model calls. No speculative environment framework or broad regression suite.

Exercise the full inherited setup, PEP723 ACP/script environment preparation,
exact role/native overlays and ordinary harmless fixture root-child-root path.
Compare actual full native prompt/sampling/ancestry against the existing CPU
contract. Qualify the second fresh container with installation network denied
or equally scoped auditable capture so absence of package fetches is evidence,
not a latency inference. Prewarm exact PEP723 script environments if necessary
within the same declared build; do not claim full offline operation from nano
.ready alone. Never execute generated model code on the host.

Publish builder/source/command/log provenance, exact base/new image identity and
archive or layer manifest, nano commit+working-file hashes, original uv.lock hash
and actual usage, Python/uv versions and binary hashes, installed distribution
versions and available artifact hashes, extras, timestamps, attempt cap, owner
state, fixture comparisons and observed setup/network timings. Mark any missing
historical/environment fields unknown. Preserve owned artifacts for resumption;
do not delete shared or ambiguous environments. Return CPU-ready evidence only.

Any eventual model comparison or new training recipe must explicitly select this
new image and scope any changed runtime wrapper. No retroactive rescue of prior
nulls, unchanged-runtime claim, automatic promotion, or modification of the
uptake/role/news/adaptive/cue jobs already accepted in this session.
