# Published RLM8B reference: CPU handoff

2026-09-10. Design only; no GPU/model service/container launched and no environment installed. MAIN-owned model downloads were not duplicated. Existing clone, accepted sources and active runtime store were not edited.

- Design: `ideas/2026-09-10-published-rlm8b-intended-scaffold.md`, SHA `57c98ded0039a0bb49565d602a654f48b3c2c0c2a223f1f8608be16e04e23273`.
- Machine-readable proposal: companion `.yaml`, SHA `8cb87316469849920c29269ebee6cffad87b0adc05e396a11253c36554248350`.
- Official historical acquisition receipt: `acquisitions/2026-09-10-rlm-official-beb0603.json`, SHA `1f8dfa3dfe5d850117ac1f4b5cab050abb35daea09043480c29195a3ca399182`;157 source-file pins reverified, zero mismatches, correct commit and clean acquired worktree.

Recommendation:48 endpoints,24 identical exposed QSR tasks per8B package,23 nonzero targets per policy,3600s outer. Intended-interface candidate is official `beb0603` with the paper-specific 8B custom prompt, not cached `854e688` whose answer dictionary is incompatible with the published FINAL protocol. The compatible commit is not asserted to be the exact training commit. Common released chat template and both policies' root+leaf weight bundle are explicit limitations.

Read-only/source findings and authored CPU probe: ordinary PATH has no Docker/Podman executable, but the qualified an27 rootless wrapper/image/store exist; a harmless `unshare --user --map-root-user --mount --pid --fork --net /usr/bin/true` passed. This is feasibility evidence, not composed isolation qualification. No downloaded Python or model-produced program was executed.

Before implementation acceptance: exact paper prompt and paired native-template materialization, isolated official root→child→root fixture, explicit capped/no-retry client, actual owner/service binding, and separate dependency qualification. Historical DockerREPL's startup installation, host-loopback proxy and unbounded subprocess are documented; no blind invocation proposed. Full design has read-depth and source hashes. Budget arithmetic verified:2×1620+90=3330work;3330+150cleanup+120margin=3600outer.

Independent loader audit remains sealed with its additive context-sign correction; this follow-up changes no prior scores or seals. This agent previously authored shared local lifecycle plumbing, not the published scaffold or weights.
