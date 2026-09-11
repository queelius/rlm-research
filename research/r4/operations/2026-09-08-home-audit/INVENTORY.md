# Home storage inventory — 2026-09-08

Status: deferred by the user after confirming available quota. This audit made no moves,
deletions, installations, or configuration changes. Only this report and the proposed path map
were written. Measurements are snapshots taken in the active `an21` / Slurm `5771` session.

## Capacity

Ceph virtual attributes expose the following quotas; `df` reports shared cluster capacity and
does not show these limits.

| Location | Byte quota | Recursive logical bytes | File quota | `ceph.dir.rfiles` |
| --- | ---: | ---: | ---: | ---: |
| `/home/atowell` | 1,099,511,627,776 (1 TiB) | 117,033,960,022 | 1,000,000 | 192,684 |
| `/project/alex_phd` | 1,099,511,627,776 (1 TiB) | 444,616,054,344 | 1,000,000 | 762,781 |

Home is about 10.6% of its byte quota. Project file-count headroom deserves attention before
copying environments or caches with many small files. Recursive file counts and allocated bytes
are different metrics; neither is a checksum inventory.

## Largest home trees

`du -x -B1` measured 117,082,866,176 allocated bytes in home (about 109.0 GiB):

| Tree | Allocated bytes | Observation |
| --- | ---: | --- |
| `.cache/huggingface/hub` | 85,503,476,736 | Five Qwen model caches; 201 recursive files, 43 subdirectories |
| `.cache/uv` | 16,637,507,584 | Package/build/Git cache; 131,410 recursive files, 19,664 subdirectories |
| `.local/share/enroot/pyxis_5771.4294967291` | 10,307,931,648 | Backs the current container root; live and excluded |
| `.codex` | 4,130,149,888 | Live executable, databases, and session files; excluded |
| `.local/share/uv` | 200,508,416 | Managed Python installations; `.local/bin/python3.12` points here |
| `.cache/pip` | 109,151,232 | Download cache; 300 recursive files, 395 subdirectories |

The complete `.cache` tree measured 102,368,859,648 bytes. `.npm` was absent. Code-server
has live log files and an IPC socket in `.local/share/code-server`; it was excluded from
migration consideration. `.codex` grows during the session, so later totals differ slightly.

## Hugging Face contents

| Model | Allocated bytes | GiB | Cached snapshot revision |
| --- | ---: | ---: | --- |
| Qwen3-14B | 29,552,599,040 | 27.52 | `40c069824f4251a91eefaf281ebe4c544efd3e18` |
| Qwen3-14B-Base | 29,548,207,616 | 27.52 | `0b0bd3732e2c374d483664439ea334928b65f304` |
| Qwen2.5-7B-Instruct | 15,242,800,128 | 14.20 | `a09a35458c702b33eeacc393d103063234e8bc28` |
| Qwen3-4B-Instruct-2507 | 8,060,907,520 | 7.51 | `cdbee75f17c01a7cc42f958dc650907174af0554` |
| Qwen2.5-1.5B-Instruct | 3,098,961,920 | 2.89 | `989aa7980e4cf806f80c7fef2b1adb7bc71aa306` |

Every entry in the hub ownership scan belonged to `atowell`. Snapshot symlinks inspected
point relatively into their model's `../../blobs/` directory. No home-cache consumer appeared
in the final local `lsof` snapshot. These observations establish local inactivity only; they
do not prove exclusive research ownership or absence of consumers on other nodes.

## Deferred future option

If home pressure returns, prioritize copying only `.cache/huggingface/hub` to
`/project/alex_phd/research-cache/huggingface-home/hub`, verifying content and symlinks,
recording the completed path map, and preserving the old path with a symlink. The proposed
destination was absent at inspection. Keeping the Hugging Face parent in home avoids moving
its credentials/configuration. No credential-bearing file was read.

Defer the uv cache until project file headroom and ownership are rechecked: its current
131,410 recursive files would raise the observed project file count to about 894,191 before
other growth. `/project/alex_phd/.cache/uv` already exists, so a future move must use a
dedicated destination instead of an unreviewed merge. Pip offers only about 104 MiB savings.

`XDG_CACHE_HOME`, Hugging Face cache overrides, `UV_CACHE_DIR`, uv installation/tool
overrides, `PIP_CACHE_DIR`, and `NPM_CONFIG_CACHE` were unset in this shell. `VIRTUAL_ENV`
was `/project/alex_phd/envs/rlm`, and `TMPDIR` was `/tmp`. A path-only search of `.bashrc`
and `.profile` found none of the inspected cache overrides.

Cluster-wide ownership remains unverified. Slurm clients at
`/export/software/system/slurm/25.05.1/bin/` failed with `Invalid user for SlurmUser slurm`
and `Unable to process configuration file` inside this container. The user deferred storage
work before any host-route investigation. Future migration must recheck all active jobs,
local consumers, destination conflicts, content hashes, and quota headroom at execution time.

The machine-readable proposal is `proposed-migration-map.json`; its entries are deferred,
unexecuted suggestions, not evidence of completed migration.
