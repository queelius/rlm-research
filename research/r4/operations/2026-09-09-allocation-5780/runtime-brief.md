# Task1: portable lifecycle for the already prepared SFT

You own ONLY a new external sidecar:
 /project/alex_phd/runs/rlm-research-r4/sidecars/runtime-an27-5780-v1
and this operation's runtime-report.md. Do not dispatch subagents, launch GPU models,
take coordinator locks, alter scientific READY, edit original source, mutate environments,
delete anything, or execute generated model programs outside the existing runtime.
No Git commit/push needed for external research artifacts. Main will review your diff.

Read first ../2026-09-09-to-48h-allocation/HANDOFF.md (relative to this brief's directory).
Then inspect sidecars/runtime-local-cache-v1/RUNBOOK.md, isolation_short.py,
copy_image.py, seal.py, bin/docker, immutable source manifests and qualified CPU fixture.
Research root is /project/alex_phd/runs/rlm-research-r4. Current node an27, UID1523821556,
CPUs0..15, memory64GiB, driver580.159.04. Old /tmp/rlmc.0m4242 does not exist.
Durable image root /project/alex_phd/research-cache/runtime-images/rpi-v2.kCaOH4/root.
Qualified image8cfe5976b347e0201e52035256537a7cc90fca5004a0bf48cbd42b282498838c.

Implement smallest additive lifecycle adaptation: mktemp-owned bounded local cache,
copy only selected immutable layers with hash mapping, own metadata, allowed CPUs14,15
(or record another allowed pair), runtime wrapper with owner checks. Same image/prompt.
Use existing fixture once after focused narrow isolation tests; no broad tests. It is
CPU fake-provider root-child-root native fixture, not GPU or training evidence.
Preserve failures; do not repeatedly run slow qualification with no hypothesis.
Read original complete-SFT binding/launch/study and identify exact injection seam for
new ROOTLESS/cache paths without editing pinned scientific sources; deliver wrapper
or precise binding plan executable under new accepted parent. Environment-only driver
adaptation should be explicit, old library path must not shadow new actual driver.
Record original-vs-new lifecycle-only diff, exact hashes, paths, tested commands and
CPU fixture output. Need a concise ready report promptly (target~10minutes), not a
production runtime rewrite. If earliest useful step can be delivered before all proof,
send it to MAIN. Use apply_patch for edits. MAIN controls launch and operation files.
