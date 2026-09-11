# Retired before launch: proposed broader curriculum duplicates completed BROAD16

Decision: MAIN retired `root-broader-curriculum-rl-v1` as a breadth successor. Its unsealed DESIGN, PLAN, two prototype modules and three CPU tests remain unchanged. There is no READY, collector/trainer/owner implementation, prepared runtime input bundle, output attempt, or GPU launch. The initial history lookup missed the completed continuation; candidate availability was incorrectly treated as evidence that its curriculum remained unrun. No GPU time was spent on this proposed successor.

## Exact comparison

Read-only comparison of the proposed in-memory plans against `root-broad-curriculum-v1/inputs` found:

| Dimension | Finding |
|---|---|
| Candidate identity | Identical `75e4fcd76174bf52762523bcde24b23580ef9a7d89c6c49eb60285df14d40154`; MANIFEST SHA `3b00b9a7ce4dd2cb086ed8937e459e852503139819d08c8e544d51f69c6bd0d6` |
| Public data / targets | All 47 used context text byte strings, all 80 question byte strings and all 80 gold records identical |
| Training schedule | All 16 windows have identical task × repeat multisets: 3 × 8 attempts/window, 384 total; same 24 training contexts |
| Validation / transfer | Same 16 validation and 48 transfer task × repeat multisets; these panels already have root-study exposure |
| Numerical recipe | No differences in 14 compared fields: learning rate, weight decay, gradient clipping, TIS cap, PPO clip, guards, base/adapter dtype, advantage normalization, loss weighting, temperature, causal cap, IS normalization and authenticated dependencies |
| Root start | Old original adapter SHA `857a7ce6907c759a8c1b478eb53029d3b700b81c3094d8edb3394e52def9fcb6`; proposed low66c is a different SFT warm start (its eight-update SFT RESULT names starting adapter `efab2913e7fe9f5f9b381ae6eb67bb56071070f86b237e6145f98654816aad64`) |
| Optimizer / seeds | Proposed fresh Adam cursor zero and optimizer seed 981371002 versus old 981268001; fresh rollout seeds, with no training seed overlap. Old continuation restored the original run's Adam/RNG chain and completed all 16 updates |
| Interface | Old standard StrictOolongTask context.txt/question interface; proposed typed-ID JSON records, correct id/user/text contract and optional typed child helper, common to both proposed policies. Frozen child weights c32 unchanged |
| Execution | Proposed four workers versus eight, explicit no-op window semantics, refined endpoint/admission distinction, new an27 runtime and six-hour envelope. Collection/training/validation stage caps 600/240/480 s versus old 1800/600/900 s; 8192 context, 2048 sampling cap and temperature 0.5 unchanged |

Thus this is not new task/operator/composition breadth. At most it could be a deliberately rescoped warm-start-plus-interface RL replication, with several simultaneous changes and previously exposed transfer inputs. The proposed accurate records/helper interface is substantive, but cannot turn reused category-count questions into new operators. No direct comparison to old percentages would isolate its cause.

## Already obtained evidence

The independent completed-continuation audit reports all 16 optimizer updates, 384 training attempts (379 admitted), 253 mixed-group episodes, 540 root turns and 171,288 trained action tokens. Fixed final16 transfer was 16/48 versus original 13/48 (eight gains, five losses); all 96 paired endpoints were observable/admitted. Composition remained 5/24 versus 5/24; 256-record outcomes remained 0/4. Final root SHA is `fa23ebc2ecd2ddec2486877d426b1c6c81d8f82262388158b33e57d96ae4b8e7`, checkpoint-state SHA `fd51f81def54dc1fad409e3bf7c00fa5ba945a5c1dc03617a2405b1860cb5c7b`. These are cited audited results, not a new raw-graph audit by this author.

The initial broad attempt's zero-update STOP is not the final scientific result: the continuation reused its first 24 retained attempts, then completed the remaining schedule. Combined scientific elapsed was 8,083.08 seconds. The continuation's recipe wrapper points to the original numerical recipe; missing top-level fields in that wrapper are not objective changes.

## Pins and recommendation

- Original READY SHA `94f416ebe6a613f4109a3648a177407f5567df574047cbb8a0e60a10ceec10a1`.
- Original PLANS SHA `c4210619e5635db210cd39339e2543f7dedbcee006f360ee0951b16063dc9786`; PUBLIC SHA `2c466164e9aaffe2571c1f83c18b394345213c82610b7fc3068282600b1eee6b`; RECIPE SHA `c15e83f9a092b0e568ef71ab3122364e1018e3543da1f3e968214c197ab1acd8`.
- Continuation READY SHA `36a5e1c2cf8ce6f1a86bbc739ccdc275f4a098953f0dcac117fe3301f3b3f48b`; FINAL SHA `7cd76930b65cc674d1d9926fc91a381e87c1dcaeabb42e5c213e64ad6f1a1066`.
- Independent report `analyses/root-broad-equality-continuation-live-2026-09-09/REPORT.md`, SHA `8c2883690f8d9c5d00f708eadba291b7f14a90741d1ab24532517d7b9bb6bfa6`.
- Retired proposed DESIGN SHA `831ff9d4f62bc4de948c7b8c1ca43c78a2eab7e2a826b85f55be1651860db1c9`.

Recommendation accepted: retire as breadth successor and design genuinely query-sensitive tasks on the same record/label structure. Separate the question of operator/composition learning from the alternative of training at genuine partial-acquisition states. Do not infer success from CE, nominal attempts, optimizer count, or the existence of a fresh runtime namespace.
