# Frozen broader AG data — data only

Manifest: `inputs/MANIFEST.json`, SHA256 `b5e9cc22161959fc09f5e1f15afd03e722a32818bca692a01f9e265fd6c81c2d`, identity `0b2e875715b80a66073fd04dc238b9182762a9cf501f90ed28d247f5e5f191f5`.

The freeze contains 1,024 new balanced training records (eight disjoint 128-record steps, 32/class/step) and 512 new balanced heldout records (128/class), all drawn from the pinned original AG train split. The heldout is separate from current AG256, old AG128, fresh AG64 and all new training records. No selected record was sent to a model. CPU tokenization is the only model-asset use.

`DESIGN.md` has YAML frontmatter specifying the namespace, schedules, seeds and heldout restrictions. `inputs/EXCLUSIONS.json` records every frozen public/root input source and the exact actual c32 training consumption check: 5,065 records, twice each, matched between prepared `train` data and checkpoint `step_metrics`. Available public input inventories are included conservatively, including unrelated dataset ID collisions; this is not a claim that every excluded input was optimized on.

Selection removed 434 rows in 217 word-normalized duplicate groups, including 28 conflicting-label groups; this subsumes 151 whitespace-normalized duplicate groups. A further 383 rows matched the frozen exclusion union, leaving 119,183 eligible. Exactly one of the previous training128+heldout256 records was already removed by the stronger duplicate filter. Selected source-ID and both normalized-text overlaps are zero.

## Consumer interfaces

- `inputs/TRAIN_PUBLIC.json` and `TRAIN_GOLD.json`: full 1,024-record corpus for a subsequently approved training procedure; labels are host-only.
- `inputs/step-001/` through `step-008/`: `PUBLIC.json`, `HOST_GOLD.json` and 128-action `REQUESTS.json` per step. The schedule is repeat-major, four actions for each of 32 B4 groups, with fixed seeds. No sampler or trainer is admitted here.
- `inputs/HELDOUT_PUBLIC.json`, `HELDOUT_GOLD.json`, `HELDOUT_REQUESTS.json`: final-endpoint-only 512-record panel, 128 B4 temperature-zero requests. Do not query it for intermediate checkpoint selection or tuning. A future RL/SFT comparison must freeze its endpoint and evaluation protocol first.
- `inputs/SELECTED_PROVENANCE.json`: exact original source row indices, IDs, text, host labels and both normalization hashes; never pass this file to a prompt builder.
- Requests preserve ordered schemas as `schema_ordered_json`. JSON files otherwise use canonical sorted maps: consumers **must restore** `body.sampling_params.structured_outputs.json = json.loads(schema_ordered_json)` before sending, as the established native collector does.

Maximum prompt+1,024 generation tokens: training **2,265**, heldout **2,187**, both below the required 8,192 context cap. No truncation or replacement was used. Runtime owners must still attest their actual service cap and binding at launch.

## CPU verification

`VERIFIED.json` records 155 source hashes and 32 artifact hashes checked, all 1,536 selected rows rederived from the parquet, exact selection reproduced, all eight schedules checked, and two focused fixtures passing in 0.11s. `TOKEN_RECHECK.json` independently rebuilds all 384 distinct prompts / 1,152 scheduled request bodies from public records and the frozen helper wrapper, checking exact token IDs, labels and schema ordering. No inference calls occurred. Initial Ruff checking found three style-only findings; it is not claimed as a passing gate, and the frozen source was not changed afterward.

Run commands used the existing native Python with `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1`: `prepare.py`, then `verify.py`, then `token_recheck.py`. The latter two write-once receipts intentionally prevent overwriting evidence. The data manifest pins Python/package versions, cache acquisition receipts, tokenizer/config and original source files.

This excludes audited local optimization exposure and known public panels, not unknown base-model pretraining. The pinned dataset card leaves licensing unspecified; no redistribution grant is inferred. Existing inputs, outputs and the earlier hashed eight-step proposal remain unchanged. This artifact grants **no optimizer or GPU admission**.
