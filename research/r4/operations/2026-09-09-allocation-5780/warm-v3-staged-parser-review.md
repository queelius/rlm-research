# Warm V3 staged audit handoff

CPU only; no GPU/model forward, process control, live-source mutation or final outcome reads. runtime_port authored V3 recovery: these are author-assisted checks, not independent V3 review. Original parser.py, METHOD/seals and the live owner's hash-bound wire_ledger.py are unchanged.

## Ready audit components

All paths below are under `analyses/root-sft24-terminal-rlvr-live-2026-09-10` in the research store.

- `NATIVE_WIRE_PROTOCOL_V4.md` SHA `dd2220378079edff0443e2bcb4cf025743bf0223534330092f3248f0deeb49c4`: prospective supplement, written while six state commits and no readout directory existed.
- `NATIVE_WIRE_READY_V4.json` SHA `36c8d3a3cafd1db43c3273749d0014c4a6c68b48798e3fcfa9024690820ad399`:19 source/qualification pins freshly verified. Parser qualification/seal finished after readout directories appeared; no final content was opened. This timing is explicit, not retroactive prelaunch registration.
- `native_wire_v4.py` SHA `c146361dfdddd227ac040d998ee3629ba3150b5c226d85c46ad21c821721adc8`: stage/request-ID ledger, actual parsed native message and final-graph reader, unchanged primary/NULL arithmetic. No fake physical-directory adaptation. Same-body distinct requests remain distinct; typed mirrors are not calls; conflicting duplicates are errors; each missing usage field stays unknown.
- `NATIVE_WIRE_QUALIFICATION_V4.json` SHA `bfb6ddb349e57ff7ff5f05ad9b364f5636e9d340e42f8277bf3f0bb4604b1c18`: actual closed window2,133 decoded native responses,24 endpoint coordinates, no source-score or wire-integrity disagreements. One absent native_response is the already source-unavailable failed endpoint, not a scorer correction.
- `checkpoint_chain_v4.py` SHA `a485ea72166a4d0af5e7803a8b8d1ccda299abc3eaf8edfceb0bfc19a982bcf3`; `CHECKPOINT_CHAIN_V4.json` SHA `d8c585a490db7c1c3981a66168bbff9592f1490fdc6a8306019268dd888ada47`:83 checkpoint/input pins freshly verified.
- `CLOSED_TRAINING_WIRE_V4.json` SHA `5f779e8a05c687c8654e4a5a29b8690f1ce41ee806a3a8964d7c5575e8923ecf`:all eight closed training stages, original attempt002 window1 counted once. Not whole-run cost.

## Focused verification

12 tests passed in0.07s:9 wire/native tests plus3 numerical/mask tests. Tests first failed before their implementations; separate regressions exposed and then verified the actual `/generate` request_id and stop→tool_calls translation, and decoded-versus-native tool arguments. The actual CPU window2 qualifier uses the existing renderer/tokenizer and no generation; native client source pins document that raw request_id becomes native id, and only parsed OK tools promote stop to tool_calls. All133 actual returned messages including arguments/branches matched. Input/output IDs/logprobs, model aliases and usage matched, with one HTTP400 counted as a failed attempt.

Fresh commands:

```
python -m pytest -q <analysis>/test_native_wire_v4.py <analysis>/test_checkpoint_chain_v4.py
CUDA_VISIBLE_DEVICES='' /project/alex_phd/envs/prime-rl-5990b1b/bin/python <analysis>/qualify_native_wire_v4.py
CUDA_VISIBLE_DEVICES='' /project/alex_phd/repos/rlm-bootstrap/.worktrees/a100-lora-roundtrip/gpu/training/.venv/bin/python <analysis>/checkpoint_chain_v4.py --output <analysis>/CHECKPOINT_CHAIN_V4.json
```

The qualifier and review outputs use exclusive creation; do not rerun to those existing filenames. Source/test hashes and exact receipts are in the19-pin seal.

## Training progress, not efficacy

Seven saved commits pass independent CPU arithmetic/payload checks:504 finite FP32 Adam moment pairs at exact ordinals1–7, lr5e-5/weight_decay0, previous adapter/config/state/optimizer/RNG hash ancestry, saved Python/CPU/CUDA RNG payloads, actual safetensor deltas versus each immediate parent, and exact current-action masks with zero child/observation credit. Recomputed within-task advantages, equal episode/root-turn mass, token TIS weights and numeric summaries agree. Selected episodes per commit:13,15,8,16,8,8,16; root-action tokens:5173,3414,1909,3182,1405,3322,2908. Actual pre-update optimizer restoration is source-backed rather than an extra model/optimizer replay; the saved payloads and ancestry were directly CPU-loaded.

Window8 is an explicit scheduling noop: completed_windows8, optimizer_steps7, no GROUP.json and no checkpoint8, policy stays exact checkpoint7. Its admission reason is reserved for the follow-on closed-training review; absent GROUP is not described as an inspected empty group. Therefore eight consumed windows are not eight updates. Original window1 was reused once without a new collection, and each later trained window had a successful service-release receipt before its trainer path. These checks neither establish reward efficacy nor authorize recipe changes.

## Closed training physical ledger

1047 confirmed attempts =798 root+249 child.1042 authenticated native completions and5 HTTP400. Known usage:2,053,924 input,112,729 output,1,941,520 cached tokens. Each field has5 unknown calls, not zero. Native input IDs sent include rejected requests:2,095,359. No unresolved dispatch intents or mirror/identity conflicts were found in these closed stages. Actual role records—not typed mirrors, raw-file counts, or absent physical folders—define occurrences.

The original unreleased owner is not rewritten: its stage is operationally closed using MAIN's pinned external cleanup receipt. Combined execution still charges381 original seconds plus V3 activity. Final readout and remaining orchestration costs are excluded from this staged total and must be added after terminal relay.

## Remaining terminal work

Wait for MAIN's terminal/release relay before opening either readout. Then preserve all96 original planned endpoints and source-export admission, authenticate every available final/native branch, audit every available program path, and distinguish requested operator/scope from child semantic errors, literal reconstruction, partial state and scalar coincidences. Report eight-cluster primitive/composition/zero/nonzero paired summaries and NULL bounds. Join all final calls—including failed/unexported work—to the1047 closed training calls, retain per-field unknowns, and obtain exact owner/parent EXIT/release closure. No sampled program is reexecuted and no outcome can alter the now-completed training recipe.
