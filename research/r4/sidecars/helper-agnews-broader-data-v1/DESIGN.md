---
schema: helper-agnews-broader-data-design-v1
status: approved-data-only-no-trainer-no-model-calls
created_utc: 2026-09-12T12:10:00Z
namespace: agnews-native-hf-eightstep-dose-v1|20260912
training_records: 1024
training_steps: 8
records_per_step: 128
heldout_records: 512
request_size: 4
native_training_seed_first: 202609123000
native_training_seed_last: 202609124023
initial_training_rng_seed: 202609125000
heldout_seed_first: 202609126000
heldout_seed_last: 202609126127
context_cap: 8192
max_completion_tokens: 1024
model_calls_authorized: false
---

# Reusable broader AG data freeze

Use only the existing pinned original AG train parquet. Select 256 training records/class and 128 heldout records/class, after excluding all current/old public panels, current training128, verified c32 SFT records and available root input IDs/text. Remove every duplicate group under either NFKC/casefold whitespace normalization or punctuation-insensitive word normalization. No downloaded code, model weights, optimizer or network service is executed.

Within each host-only label stratum sort by SHA256(namespace + `|candidate|` + source ID); first 256 train, next 128 heldout. Split each class's selected train order into eight consecutive 32-record allocations. Within each step order only by SHA256(namespace + `|step-NNN|` + source ID), then form consecutive four-record requests. Heldout uses its own label-blind `|heldout|` order. Gold labels never enter prompt construction or ordering keys.

Freeze eight repeat-major training schedules: 32 groups × four sampled completions per step, native seed `202609123000 + 128*(step-1) + 4*group + repeat`. The prospective training RNG seed is `202609125000`, with NumPy modulo 2**32. Heldout has 128 temperature-zero B4 requests with seeds 202609126000–202609126127. Both use the established full-category labels/definitions, keyed ordered schema and original helper chat wrapper. Tokenize every exact prompt on CPU and require prompt length +1024 ≤8192 without truncation or outcome-based replacement.

The heldout512 is separate from current AG256 and remains unqueried by models until a predeclared final endpoint. It can support a subsequently specified RL-versus-SFT comparison; no endpoint or training procedure is admitted by this data freeze. Selected provenance and host gold are analysis/training-reward inputs, not prompt inputs. This excludes audited local training exposure and known panels, not unknown base pretraining. Dataset license remains unknown/unspecified in the pinned card; no redistribution permission is inferred.

Outputs: public/gold split files; eight step inventories and 128-action schedules; heldout request schedule; exact source row indices/text/normalization provenance; rejection inventory and source pins; CPU token bounds; final content-addressed manifest. Keep all old sources and outputs unchanged. The earlier hashed eight-step proposal is preserved; this new design replaces its proposed reused AG256 primary with a distinct fresh512 option, without authorizing a trainer.
