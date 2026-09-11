# One isolated CPU preinstallation proof

Owner: /root/padding_control_prepare, under main's PREINSTALLED_RUNTIME_CPU_DECISION.md.
All new writes remain in this sidecar or newly created external storage
`/project/alex_phd/research-cache/runtime-images/rpi-v1.WHYd2G` (mktemp, initially empty).
Host HOME/CODEX_HOME are never reassigned. Existing Podman root/runroot/image tags are not writable targets.

Sequence: focused isolation tests; private Podman isolation check; exact immutable base export/read and private load; one original harness install and exact PEP723 preparation; record package/source/binary state and commit new image only in private storage; at most two fresh native root-child-root CPU fixtures, the second with installation network denied/scoped evidence; seal result or stop on material failure with no rebuild/retry.

One build attempt is capped at900s including export/load/setup/prewarm/image work, with two CPU workers. Each fresh fixture is capped180s. No model/GPU calls. No accepted image/config/source changes. Setup failure is a preserved CPU feasibility outcome, not a reason to change live infrastructure. Scope remains fixed even if initialization fails. Image53a70288e91a75c9bc8cbc9a75da4c3d156227266fd8c6c997deb8ef7f921552 and nano version-string4ef3438/full commit4ef3438d55fdd39b18d34035833c73e13b006733 are mandatory.

Initial host filesystem checks: project Ceph available489332095844352 bytes; /tmp available265536716800 bytes. UID1523821556 owns new namespace. Read-only checks observed existing shared runtime processes; none will be signaled. External VFS storage feasibility remains to be established before image export/build.
