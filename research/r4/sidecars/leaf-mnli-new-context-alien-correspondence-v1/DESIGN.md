# Approved direct new-context requested-tag mechanism replication

Binding design: `ideas/2026-09-10-mnli-new-context-alien-replication-design.md`, SHA
`22aa944b78281932a23e5ed3c6a37d77bfb90b98ccf3c6aeb444345c9cebacf8`.

MAIN approved CPU implementation only: 16 newly selected MNLI48 contexts, one paired seed each,
matching/shift17/alien exact-tag arms, 48 calls, released cdbee base, no adapter/tools, 3072/8192.
Selection master 981622001; seeds 981622101--116. Preserve 6/5/5 first-arm imbalance, label-blind
selection, named-inventory collision bounds, native NULLs and whole-contract primary scoring. MAIN
alone owns GPU launch.
