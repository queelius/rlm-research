# Hard-curriculum one-update RLM RLVR sidecar

Date: 2026-09-02

## Purpose and status

This sidecar is an exploratory, provenance-sealed follow-up to
`rlvr-e2e-pilot-v1/attempt-002`. That attempt produced 72 calibration episodes: 66 valid
episodes with 66 exact successes and six invalid episodes. It therefore could not form a
mixed-reward training group. This study changes task difficulty, not malformed-output policy,
to find a learnable coordinate and execute exactly one masked LoRA policy-gradient update.

The study is not a capability claim. CPU fixtures validate engineering contracts only. Only a
sealed GPU attempt that passes every launch and analysis gate may produce research evidence.

## Immutable inputs

The manifest authenticates these inputs before attempt creation and again before every phase:

- Qwen3-8B model bundle
  `a6e808bea6314528485065e7e197c177246839851c02ed9609e002a85b1ddb88`, including its
  bundle row inventory, tokenizer SHA-256
  `aeb13307a71acd8fe81861d94ad54ab689df773318809eed3cbe794b4492dae4`, and model shard
  inventory.
- Adaptive SFT checkpoint `rlm-adaptive-sft-adaptive-s2908202707-k576`, adapter weights
  SHA-256 `8a20ec86ff48f519294614178f79ace582b89c3ae0b5524b1639b4940edbb14d` and adapter config
  SHA-256 `775f87282a7b7e682a363a82ef170091f0b540324847016e36dd94095d579eff`.
- `rlm` commit `3aeb99d2a6ff125868f0329bfea584de84c1f715` and `rlm-bootstrap` commit
  `9a095c96585c96e387986f6afa5ce2d1d631d232`.
- Proven pilot driver SHA-256 `e4308121c8a0d7bf89c2a6cb6c99cdde48a5e688a6d370e84bbe70eb96aac93b`
  and core SHA-256 `22651b1670538f0eb7d2a0cd221f99be43ce1d5f9d43ca784db269e614f6e411`.

The new sidecar vendors the small proven driver/core paths instead of importing mutable prior
files. The manifest records both the upstream hashes and every sidecar source hash. The model
bundle and old adapter remain read-only. Base shard hashes are captured before and after the
update and must be identical.

## Curriculum generator

The generator is pure, deterministic, and versioned. A task identity binds the generator
version, split, rung, task seed, complete prompt, normalized private gold, and endpoint schema.
Calibration and held-out seed namespaces are disjoint. The generator never reads model output.

Every task preserves the controller's learned envelope:

1. instruction to use Python for visible structure and a semantic model only for semantic
   classification;
2. an opaque label ontology;
3. indexed records with visible mechanical attributes and a natural-language semantic clause;
4. a count query;
5. exact `{"kind":"count","value":<integer>}` output instructions.

Semantic classes are assigned from frozen, unambiguous template families. Subtle classes use
close but operationally distinct definitions, such as actor versus owner and event location
versus storage location. The private verifier recomputes eligibility and semantic membership
from the sealed structured records; it does not trust a stored answer alone.

The five ordered task-only rungs all use controller temperature 0.8:

| Rung | Records | Labels | Additional difficulty |
| --- | ---: | ---: | --- |
| `r1` | 96 | 8 | facet and one target semantic label |
| `r2` | 128 | 10 | close actor/owner and event/storage boundaries |
| `r3` | 160 | 12 | facet plus record-index residue eligibility |
| `r4` | 192 | 12 | nested conjunction with a visible flag disjunction |
| `r5` | 224 | 14 | nested complement and membership in two target labels |

Difficulty changes only along this frozen order. Temperature is not searched. Real tokenizer
preflight counts every public prompt and rejects any task whose complete root prompt plus the
2,048-token controller allowance and fixed runtime overhead cannot fit the 8,192-token server
window. It also regenerates every task and verifier answer byte-for-byte.

## Calibration and coordinate selection

Each rung contains four calibration tasks and six rollout seeds per task: 24 episodes. Rungs
run sequentially. At most 120 calibration episodes are allowed. An early decision is allowed
only after every one of a rung's 24 planned episode identities is durably terminal. Scheduling
or restart order cannot affect admission.

For training, a valid terminal response is exactly one schema-conforming JSON count object.
A valid correct answer has reward 1; a valid wrong integer has reward 0. Timeout, model failure,
turn-limit exhaustion, malformed JSON, wrong schema, extra text, and missing output are invalid,
have `reward: null`, and are excluded. No invalid trajectory is ever converted to a negative or
zero training reward.

The first complete rung is admitted only when all of these frozen rules hold:

- at least 20 of 24 trajectories are valid;
- success among valid trajectories is between 20% and 80%, inclusive;
- at least two task/prompt groups each contain at least four valid trajectories and both reward
  values.

If no rung qualifies, the attempt stops without training. Within the admitted rung, every valid
trajectory from every eligible mixed prompt group is used. Rewards are population-standardized
within prompt group. Non-mixed and invalid groups contribute no examples. This preserves the
prompt-group interpretation of policy-gradient advantages and avoids outcome-based selection of
a favorable individual prompt.

## Policy data and exactly one update

The vLLM launch retains `--return-tokens-as-token-ids`, selected-token logprobs, the tested
short Unix RPC root `/tmp/rlvr-<sha256(server-artifact-root)[:16]>`, and its narrowly scoped
cleanup. A launch-contract probe confirms that raw action token IDs match the logprob token IDs
before calibration; the probe is excluded from all estimates.

Each controller turn stores the complete prompt token IDs, action token IDs, selected-token old
logprobs, action text, trace identity, and leaf request/response hashes. Loss labels and masks are
zero/`-100` for every prompt, observation, environment, and leaf token and one only for root
controller action tokens. Leaf outputs are context, never policy actions.

The one update uses the proven clipped objective: within-prompt standardized advantages,
epsilon 0.2, beta 0, AdamW learning rate `5e-6`, mean action-token loss then mean turns/groups,
and exactly one optimizer step. Before stepping, recomputed old-policy logprobs must differ from
captured logprobs by at most 0.5 maximum and 0.1 mean absolute error. The update fails closed on
token/logprob misalignment, any nonfinite value, zero or nonfinite gradient, mask violation,
unexpected trainable parameters, or optimizer state inconsistent with step one.

Completion requires all of the following evidence:

- finite positive pre-clip gradient norm;
- controller action token count positive and every non-controller mask entry zero;
- at least one LoRA tensor changed and finite parameter-delta norm is positive;
- old and new adapter file hashes differ;
- every base-model shard hash is unchanged;
- saved adapter/config/optimizer/RNG hashes are recorded;
- the saved adapter metadata is reload-compatible with the sealed base;
- the durable training marker records one optimizer step and makes a second step impossible.

## Held-out paired evaluation

Eight held-out task seeds are generated independently at the selected rung. Three fixed rollout
seeds yield 24 sealed pairs. Old and new policies receive the same task, seed, temperature 0.8,
budgets, and runtime. Pre-evaluation completes before training or is otherwise served from a
separately authenticated old-policy server; post-evaluation uses only the new adapter.

The primary endpoint is paired terminal success over all 24 pairs. A valid exact answer is 1;
every other terminal outcome, including invalid trajectories, is 0 for this evaluation endpoint
only. The primary estimate is the mean of `post_success - pre_success` over the 24 sealed pairs,
with all pair-level outcomes retained. This evaluation accounting does not create training
rewards.

Secondary decompositions report jointly-valid exact delta, validity delta, transition counts,
and invalid-reason counts by arm. They are descriptive and cannot replace the primary endpoint.

## Durable attempts and failure behavior

`prepare` creates a new attempt directory and atomically writes read-only spec, task inventory,
endpoint descriptor, and launch descriptor. It refuses an existing path. `run --resume` accepts
only an existing attempt whose source, manifest, inputs, task regeneration, and phase history all
authenticate. Episodes are content-addressed individual JSON files plus an append-only index.

Each phase has a terminal marker whose inputs bind all preceding artifacts. Resume skips a phase
only after validating its complete marker and outputs. A partial update, contradictory marker,
duplicate episode with different bytes, missing planned identity, changed launch descriptor, or
attempt after a terminal failure causes a machine-readable refusal. The driver writes either a
completed result or a failure record; it never overwrites research artifacts.

The phases are: provenance probe, task preparation, contract probe, rung-by-rung calibration,
selection, held-out pre-evaluation, one update, held-out post-evaluation, paired analysis. The
90-minute wall-clock stop remains enforced, alongside the 120-episode calibration maximum.

## Sidecar layout and verification

- `source/curriculum.py`: pure generator, verifier, admission, pairing, and state contracts.
- `source/rlvr_hard_curriculum.py`: provenance, runtime orchestration, token capture, update, and
  CLI.
- `source/test_curriculum.py` and `source/test_rlvr_hard_curriculum.py`: CPU tests.
- `fixtures/`: explicitly engineering-only examples; never accepted as research evidence.
- `manifest.json`: authenticated inputs, source inventory, commands, and design hash.
- `launch.json`: exact deferred GPU command and environment contract.
- `RUNBOOK.md`: preparation, preflight, launch, resume, audit, and interpretation.

TDD tests cover deterministic task/gold regeneration, split isolation, monotone rung shapes,
token-window refusal, invalid-null reward semantics, full-rung admission, no early partial-rung
selection, per-prompt advantages, root-only masks, logprob token alignment, drift gates,
one-step/update/hash evidence, durable resume/refusal cases, all-24 primary pairing, and exclusion
of fixtures from research analysis. GPU behavior is represented only through narrow CPU fakes;
preflight never opens a port or initializes CUDA.

