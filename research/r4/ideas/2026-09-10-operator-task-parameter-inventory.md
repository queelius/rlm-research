# Operator demonstration task-parameter inventory

2026-09-10. Read-only diagnosis, not a new experiment approval. I authored the operator corpus plumbing and common native runtime; this is source diagnosis, not an independent efficacy audit. The reported teacher-first syntax counts were supplied by MAIN. I did not rescore probes, read the new free outcomes, execute sampled code, or change scientific sources.

## Finding

**Width 4/16 is an authored demonstration coordinate, not an instructed maximum batch size.** Neither the actual root prompt nor `query.txt` specifies `max_batch`. A generated slice of 16 on a width-4 demonstration prefix is not instruction noncompliance. It may be a legal alternative acquisition strategy; whether it works requires actual execution and finishing, which the first-action probes do not establish.

| Parameter | Actual root-visible representation | Authored target use |
|---|---|---|
| Operator | Natural-language count, distinct-user count, or visible-weight sum in the question | Host selects `len`, set cardinality, or `sum` Python expression |
| Scope/users | Natural-language all/single/union scope in question and identical `query.txt` | Concrete user list in reduction predicate |
| Target category | Canonical category string in the question; definitions in common prompt | Literal category comparison against actual child predictions |
| Source path/schema | Prompt names `records.json`, `context.txt`, four public fields, and optional `batch_contract.py` | Literal `open("records.json")`, fixed field keys |
| Batch width | Private training row and capture schedule only; no runtime instruction/limit | Literal slices `[0:4]` … `[12:16]`, or `[0:16]` |
| Variable names | First introduced by authored Python, then genuine REPL state | Four concrete alias layouts; no hidden variable reconstruction |

There is no exposed canonical machine-readable **task-parameter** specification. The public records are machine-readable data, not a task specification. `query.txt` is prose. The actual qualified free-task setup receipt lists exactly `batch_contract.py`, `context.txt`, `query.txt`, and `records.json` for all 48 dose-readout task coordinates. The controller is `free`, so the inherited setup does not write `operator_config.json` or `operator_program.py`. Private row metadata and `task.data.source_split` are not a substitute for model-visible instructions.

The full targets do not read task parameters from a metadata file. They nevertheless perform genuine computation: producer actions acquire actual c32 predictions and update a live map; reduction reads that map and public records. Literal target categories/users are query parameters, not copied gold labels. Native stop targets use the scalar actually printed, including errors inherited from child predictions.

## Actual corpus and objective check

Read all 72 `TEACHER.json` files and verified each against `capture/CORPUS_READY.json`; all 72 first-action prefixes equal the frozen `PROMPTS_ACCURATE.json` native token IDs. There are **62 distinct first prefixes and 10 duplicate pairs**. Each duplicate pair has the same width. Parsing (not executing) their authored first actions and canonicalizing the declared variable aliases gives identical ASTs in all 10 pairs. There are zero equal-prefix pairs with different widths. Therefore the observed duplicates are alpha-equivalent legal demonstrations, not demonstrated incompatible batching instructions. Different file contents can share a pre-file-load prompt.

Within a context/query, width also rotates the prose template and alias layout. This prevents treating width as an isolated prompt factor. More generally, multiple valid strategies under similar tasks are not contradictions merely because exact next-token targets differ.

There are 36 width-4 episodes with four producer actions each and 36 width-16 episodes with one producer each: 180 producer actions, 72 reductions, 72 stops, 324 total. Per-episode masses are `.45` producers, `.50` reduction, `.05` stop. Producer mass is shared equally among that episode's producers. Thus a width-4 first action has nominal mass `.1125/72 = .0015625`, versus `.45/72 = .00625` for width 16: **4× nominal first-action weighting for width 16**. Across the corpus, first actions receive `.28125` mass; later width-4 producer actions receive `.16875`. Each width stratum still receives `.225` total producer mass. These are coefficients on action-mean CE, not measured gradient contributions, equal-token weighting, or proof of a cause for sampled behavior.

The current-action suffix is fully trained, including literals and transport format. All prior prompt/observations are masked. `copied_literals` versus `mechanism` spans separate NLL diagnostics only; they do not remove literals from the training objective. Each complete update traverses the same frozen corpus and repeats these coefficients.

## Decision

Do not launch a batching “repair” experiment from these probes. First distinguish actual acquisition initiation, subsequent state use, and finishing on the pending free readout. Exact demonstrator-width reproduction is not the scientific success criterion.

Only if that readout shows genuine **operator/scope binding** failures, one discriminating follow-up would be a fixed-policy, paired 24-endpoint task-interface pilot: 12 declared tasks with the existing accurate prose versus the same prose plus a documented `task.json` containing only operator, users, category, and source path. Keep raw files, role, child, tasks, and paired seeds common; no batch limit, algorithm, map, restored state, example solution, or gold. Measure actual metadata retrieval, executed parameter fidelity, acquisition, strict final accuracy/NULLs, and physical costs separately. This tests whether a redundant machine-readable parameter interface is sufficient without new on-policy training. Failure would not prove state-coverage causality. It differs from field/map clarity and canonical loaders: it changes task-parameter access, not record semantics, acquired evidence, or restoration of Python state. This is conditional design only, not a requested implementation or priority over the free-readout diagnosis.

## Exact sources and pins

Paths below are relative to `/project/alex_phd/runs/rlm-research-r4`. Complete current operator protocol/study/collector/learning, QSR prompt/task source, qualified joint learning, current-action loss, and teacher-probe source were read; the inherited setup method and the actual setup receipt were inspected. No broad historical outcome audit was performed.

| Source | SHA-256 |
|---|---|
| `sidecars/root-operator-diverse-sft-v1/od_protocol.py` | `1ee6f9c71addfbf4f6e5f47f52ea2547bddf5cb8979d67ffb86cd3e88adc5acc` |
| `sidecars/root-operator-diverse-sft-v1/od_study.py` | `3d437ec69d3a1f0dfa038e5c7bbd7dcd770c512b39660385cc9a6759e29d2143` |
| `sidecars/root-operator-diverse-sft-v1/od_collect.py` | `b9e4efae5ba855c6d5196843c1a483fbc8a0cb583acdc56846bfdde01d35a1ae` |
| `sidecars/root-operator-diverse-sft-v1/od_learning.py` | `519bb7e693eff398d8eb06b6049aa3163e73bca620e465c36e34af80ee27e8ad` |
| `sidecars/root-operator-diverse-sft-v1/inputs/TRAIN_PLAN.json` | `ee5a741af0a96c60d9e8ea5972d4b560ac8ad8ff7f5908db76da7fc0af3e6869` |
| `sidecars/root-operator-diverse-sft-v1/inputs/FREE_PLAN.json` | `c25cc7eaae0021d01db57a0bb43896a8a0eb409c7f869ba5ae6b056732464225` |
| `sidecars/root-operator-diverse-sft-v1/inputs/PROMPTS_ACCURATE.json` | `446b69cdb2183f8742e2bc43ff0d8837967a958c01d5d7d872d38fd872d91577` |
| `sidecars/root-operator-diverse-sft-v1/outputs/attempt-001/capture/CORPUS_READY.json` | `207d36997fe82c390a82e3b27c4e3ad863ba5fdc07f00574cbd2084e80792ea9` |
| `sidecars/root-query-sensitive-rl-v1/qsr_native.py` | `02aea033ef02a215577af03e18769adda0d9994e947900b310b1a7ee8356441c` |
| `sidecars/root-joint-state-reduction-sft-v1/joint_learning.py` | `b5d063afe883d1cbaa49a6b50bfa9d0ca561815fdc2d1617e905724dcb69b4db` |
| `sidecars/root-corrective-reduction-sft-v1/learning.py` | `02599e6d4c49c67e5ffab7a617fc01055cebdb10bcb1eb16e63151d51326936b` |
| `sidecars/adaptive-filter-pilot-v1/experiment.py` | `ed7f94db1cb2d6b6ce30c4d78999fdc6b722f6195c39092429a029379f52e32d` |
| `sidecars/root-operator-dose-readout-v1/dr_probe.py` | `c2023ffd1d4485807ed47ef15163ae5e0a26780b45c509d861898f0deb620c02` |
| `sidecars/root-operator-dose-readout-v1/inputs/TEACHER_FIRST_REQUESTS.json` | `5395f4a99b1f7c31ee40af4e06bab34486331ea8619626d22aebc1fd0f165c1b` |
| `sidecars/root-operator-dose-readout-v1/CPU_INPUT_NATIVE.json` | `103b0304d53091448df5107c48cf493807d9dce530c28617131ae00db3d78bea` |

The canonical sorted compact JSON map of the 72 absolute teacher paths to verified hashes has SHA-256 `c667415e73bf9735087ec0f5361b4d534d08d9c5b332f9a922b020f2a99b77f0`; its entries are already retained in the pinned corpus receipt. Example width-4/16 paired IDs: `86cb2bb23a54aef0029f5bae236917871c9ff429389658711e95918c1d7323c9` and `eeff2539cebb1420f00aee45e1d98a4ace798aec9d81b19be2746fca1bc04632` under that capture directory.
