# Fresh public-normalization replication: CPU preparation only

Question: does unchanged mechanical normalization improve eligibility decisions on new same-family stages, including greater applied-change history? This is not learned decomposition, a new dataset, or a token-cost-matched intervention.

Freeze 12 new roots, one local stage per root, no outcome/eligibility filtering. History-depth 1: widths 6/12/20, two stages each, stage indices rotated 0/1, 2/0, 1/2. History-depth 3: widths 6/12, three stages each (indices 0/1/2). Only change-history depth varies; check revisions stay 1. Other structural settings exactly match prior held9: format count 3, required features 1, chain topology, same level name. Roots and all candidate IDs must be disjoint from original source, prior width panel and held9, and from each other.

Generation seeds 202609360000..11; sampling seeds 202609370000..23, two per stage, same within raw/normalized pairs. Fresh raw controls, identical prior raw rendering/IDs-only contract and exact pinned public normalizer. All candidates retained; no eligibility calculation, host-label access or root answer in prompts. Gold is computed only after all public prompts/requests are frozen, with two independent solvers checked.

All 48 calls: released Qwen3-4B-Instruct-2507, no adapter, T=.5, output384, input+output≤8192, four stage workers. Token audit covers every prefix prospectively. Any overflow stops before GPU; no automatic example replacement or width change. Natural cost one call per answer in both arms; input lengths are not matched and explanatory wording jointly changes with representation. Caps science600/owner700/external800 seconds.

Primary unordered known unique-ID exact; per-stage/width/history BA and micro precision/recall with explicit valid-set denominators. Sorted strict format is separate. Invalid-known and unknown remain separate; no output repair. Native canonical JSON response hashes and raw response file bytes have distinct meanings.

Prepare: `CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/python prepare.py`. Two focused tests cover fresh stage/history/retained-ID/token budgets and an actual localhost HTTP pair through the current owner/collector/decoder/metrics binding. Only reviewed local Python source is compiled for thin adapters; never execute model-generated code.

MAIN reviews CPU_READY and alone launches its argv under the GPU flock. This preparation launches no model/GPU work. Preserve all attempts. Analyze all 12 stage units, not 24 independent contexts, and keep prior held9 separate.
