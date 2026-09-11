# Free-emitted-ID correspondence successor

CPU preparation completed without a GPU, model, service, lock, or queue action. The runnable sidecar
is `/project/alex_phd/runs/rlm-research-r4/sidecars/leaf-free-id-correspondence-v1`.

## Prior overlap and decision

No completed study asks this exact question on released adapter-free Qwen3-4B and the frozen
fresh96 AG News/SST-2 contexts. Fresh96, identity-factorial, shifted-cue, and cue-order experiments
all force tag values and cardinality with exact grammars. The September 8 free long-batch study uses
anonymous plain-label arrays, not freely emitted source IDs.

The closest overlap is the completed indexed-followup study: mixed-size B emits free batch-local
ID-to-label maps at 373/384 item accuracy on six long TREC contexts, whereas the old trained child
selects tool mode and has no valid indexed outputs. That study uses research-trained adapters,
batch-local IDs, different contexts and greedy direct HF generation. It establishes feasibility and
a model/harness interaction, not the requested released-model effect.

MAIN approved a new all-condition run rather than reusing old exact outcomes because one new
same-service stage provides the clean decoder pairing.

## Frozen experiment

The design has 96 real calls:

- output representation: matching source-ID objects, constant `p0000` objects, or plain labels;
- decoder: free generation or the identical existing exact grammar;
- data: four frozen fresh96 AG contexts and four frozen fresh96 SST contexts;
- sampling: the original seeds 981318011 and 981318021, temperature 0.5 and full support; and
- model: released `Qwen3-4B-Instruct-2507` revision
  `cdbee75f17c01a7cc42f958dc650907174af0554`, without an adapter.

Each free/exact pair has identical messages, tools, sampling and model alias; the free request removes
only `structured_outputs`. Decoder order alternates within adjacent pairs. The run uses four workers,
a 3,072-token per-call maximum, a 1,500-second collector cap, 1,680-second shared startup/work cap,
1,770-second inclusive owned cap, and 1,800-second outer cap. The largest frozen native prompt plus
the output allowance is 7,915 tokens, within the 8,192-token service context.

Primary reporting is conservative on the planned denominator. A completed malformed or otherwise
invalid whole response is an observed policy failure and contributes zero strict correct labels. A
missing or infrastructure response is NULL and receives explicit lower/upper bounds. Conditional
label-only position accuracy is secondary. Wrong emitted IDs, ID omissions, duplicates, extra IDs,
field order, constant-tag conformance, full-shape validity, and label correctness are stored
separately. IDs never reorder or repair labels; there is no prefix rescue or answer normalization.

The free matching-versus-constant comparison is not a single-variable semantic-ID ablation because
64 distinct IDs differ in generation difficulty and cost from one repeated tag. Within each output
arm, free versus exact isolates decoder support. The reused contexts and seeds are explicitly exposed
paired data, not an independent fresh replication.

## Implementation and lifecycle

`DATA.json`, `REQUESTS.json`, `PROMPT_IDS.json`, `DISPATCH.json`, `WEIGHTS.json`, and `SPEC.json`
freeze the complete grid, exact source-coordinate joins, requests, native renderer identities,
no-adapter model binding, and scoring rules. Every exact request is byte-equivalent to its fresh96
source request; every free request differs only by removing structured output.

The source-pinned allocation lifecycle uses `service_wrapper_v2.py` in the new sidecar. This is the
base-model counterpart of the allocation's actual-wrapper-v2 fix: it adapts the pinned released-base
scientific launcher to the node's 580.159.04 driver library and reports the wrapper's actual path/hash
symmetrically to V2 ownership checks. The runtime's LoRA-specific `service_wrapper_v2.py` cannot
itself launch a no-adapter alternate base, so it is not misrepresented as the scientific launcher;
its complete `LIFECYCLE_READY_V2.json` source closure is authenticated and the same V2 claim/release
checks are installed against the new exact wrapper.

Before any output directory or process creation, `owner.py` runs the existing pinned private
credential preflight. The credential value is never returned, serialized, printed, or passed in argv.
There is no automatic retry. MAIN owns acceptance, GPU/lock admission, launch, cleanup review and
successor handoff.

## Verification

Seven focused CPU tests pass. They cover the exact 96-call 3×2×2×4×2 grid, within-arm request
pairing, malformed-completed versus missing scoring, positional scoring without ID reordering,
duplicate/omitted ID separation, credential-before-output behavior, and actual-wrapper source/driver
adaptation. `owner.py verify` also passes with no GPU or credential access and reauthenticates 34
source/input/runtime pins, all 96 request bodies and hashes, model shard stat identities, the frozen
design, and READY identity.

Key identities:

- `READY.json` SHA-256: `d2500d2502028cf2596e59247376a8157c2cffe9a34ef422484aeefaa47904d4`
- READY identity: `14a52c738dca626df0b3394d0c1346f9b67e4af7158b665fe858ae238e3eb577`
- `SPEC.json` SHA-256: `a511d51f72069d287877e554b18ff7b893aedeaee1165035c310868116ba3e77`
- `DATA.json` SHA-256: `c2e89ba70bc40c2b83eb4a1ca6d5a6e9f42c0fac13ec8e420e489c6432d22d74`
- `REQUESTS.json` SHA-256: `bc23e3cf1ff8aee85e4e51ad7663aab06f2f942afde017c08ad5df7e65faa48e`
- `CPU_TESTS.json` SHA-256: `d1f7bedda923799f6d1e1fe2fa363a9d8f27d420be533dcd9e2d2315595097ee`

`READY.json` contains the exact verify and run argv. `outputs/attempt-001` is absent. This is
CPU-ready for MAIN acceptance, not launched and not an experimental result.

## Additive launch-contract amendment

MAIN's prelaunch review found that V1's full-shape check did not require the emitted tags to match
the expected IDs or constant, and that its owner passed the shared work deadline directly to the
collector. The unaccepted, unlaunched `READY.json` above remains immutable history, but
`READY_V2.json` supersedes it for launch.

V2 makes contract-valid correct labels on the planned denominator the headline primary. A matching
object response is contract-valid only with the complete ordered schema, exact expected ID at every
position, no duplicate/missing/extra IDs, and canonical positional labels. A constant-tag response
additionally requires `p0000` at every position. A plain-label response requires its complete ordered
label array. Completed contract-invalid output is an observed policy failure worth zero headline
correct labels; infrastructure-missing output is NULL with `[0, 64]` bounds. Shape validity,
positional label correctness, wrong and position-matched IDs, omissions, duplicates, extras, field
order, and conditional label-only accuracy remain separate diagnostics. IDs are never used to reorder
or repair answers. This is the primary because the question concerns a *usable* freely emitted ID
mapping: correct labels paired with unusable IDs do not establish that correspondence survives.

The amended owner passes the collector
`min(shared absolute work deadline, collection start + 1500 seconds)`, so service startup cannot
consume or shift the explicit 1,500-second collection ceiling. It retains the V1 outer, owned, and
shared-work bounds.

V2 also directly hashes and verifies 12 inherited auxiliary sources: the inference replica template
and launcher, plus the released model's manifest, config, generation config, safetensors index,
tokenizer JSON/config, vocabulary, merges, license, and README. The V1 three-shard stat identities
remain the tensor check; no unnecessary full tensor rescan was performed.

Eleven focused CPU tests pass across V1 and the additive scoring/deadline behavior. A fresh
`owner_v2.py verify` passed, authenticating all 54 V2 source entries, all inherited requests and
native prompt-renderer identities, the auxiliary files, model shard stat identities, and amended
READY identity. No GPU, model, service, lock, or queue action occurred during preparation, and
`outputs/attempt-001` was still absent at verification.

Amended identities and launch command:

- `READY_V2.json` SHA-256: `754540d9f1940a9dcdad581838ca5b5ff090b0b36f73d0bbbfdb66623fcc9837`
- READY V2 identity: `c68fa3e51dfbc6e4c0c6139e45ffd142e0c7baaf59da1e03c4f516c8c57baf67`
- preserved V1 READY SHA-256: `d2500d2502028cf2596e59247376a8157c2cffe9a34ef422484aeefaa47904d4`
- run: `/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-free-id-correspondence-v1/owner_v2.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-free-id-correspondence-v1/outputs/attempt-001`

MAIN must privately export a nonempty `STRICT_RLM_CALIBRATION_API_KEY` before verify/run. The
credential preflight still occurs before output creation, and its value is never serialized. The
amended preparation is CPU-ready for MAIN acceptance; it is not itself an experimental result.

## Attempt-001 startup failure and additive recovery

MAIN launched the accepted V2 manifest at 19:13:24 UTC. `attempt-001` terminated after 0.726
seconds, before model startup and before the collector; its collector status is NULL. The owned
launcher and all captured descendants exited, the service ports were free, and ownership released
cleanly. This is an infrastructure/startup observation, not one of the 96 experimental outcomes.
The complete attempt directory is retained without modification.

The retained launcher traceback identifies a precise cause: the inherited released-base `serve.py`
looked up `scripts/launch.py` in the preserved V1 `SPEC.source_sha256` mapping. V2 directly pinned
and verified that launcher in its READY closure, but V1's SPEC map does not contain that key, so the
consumer raised `KeyError` before starting the inference process.

`READY_RECOVERY.json` is an additive attempt-002 recovery. `service_wrapper_v3.py` changes only the
failed consumer seam: it verifies `scripts/launch.py` against the same already-frozen SHA-256
`d511492f9add5a8bcd7325b7899bf844febe95512aa7c562f0666c9191d6609a` directly. The allocation
driver adaptation, V2 process-ownership lifecycle, model and auxiliary pins, contract-valid scoring,
1,500-second collector cap, all 96 requests, contexts, seeds, dispatch order, and sampling are
unchanged. There are no rerolls.

Fourteen focused CPU tests pass, and fresh `owner_v3.py verify` authenticated 65 source/evidence
entries plus the unchanged request, renderer, auxiliary, and model-stat closure. `attempt-002` was
absent at verification. Recovery preparation used no GPU, model, service, lock, or queue action.

- `READY_RECOVERY.json` SHA-256: `04b6db524b63f4bc3ffa5c152720c1c5ac21f63c5f4c01b4e3b63b105b09d96f`
- recovery READY identity: `c561ab4aaac1122ce20c3f1c1efd7a1e7a4b66ffc9e2838110b006a2ccb6efff`
- run: `/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-free-id-correspondence-v1/owner_v3.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-free-id-correspondence-v1/outputs/attempt-002`

As before, MAIN must privately export the nonempty credential and owns GPU/lock acceptance and
launch. The recovery READY is preparation, not an experimental result.

## Attempt-002 collector-path failure and attempt-003 recovery

Attempt-002 passed actual service startup and live preflight, then failed before its first request
because the frozen collector still authorized only `attempt-001/rollout` while the recovered owner
supplied `attempt-002/rollout`. It has no rollout `STATUS.json`; its collector status is NULL, and
the owned service released cleanly. This is a pre-request infrastructure failure, not an
experimental outcome, and both failed attempts remain retained.

`READY_RECOVERY3.json` fixes only this remaining path consumer. `driver_v3.py` preserves V2 scoring
and strictly authorizes `attempt-003/rollout`; `owner_v4.py` composes that exact destination and
validates the full owner-to-driver argv before launching the collector. The narrow CPU composition
regression accepts attempt-003 and rejects attempt-002. Fresh transitive owner verification passed.
`service_wrapper_v3.py`, `lifecycle_adapter_v3.py`, all 96 requests, seeds, contexts, sampling,
scoring, and deadlines are unchanged; there are no response rerolls.

- `READY_RECOVERY3.json` SHA-256: `6c8bc0e573820c9df9032a3b95a146c87116d36a3bb8f56b87311d343eca38ea`
- attempt-003 READY identity: `6d37e9f0c5897da397ac54a3abd2f94578832e94b18adb2a3db8f430961a913f`
- run: `/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-free-id-correspondence-v1/owner_v4.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/leaf-free-id-correspondence-v1/outputs/attempt-003`
