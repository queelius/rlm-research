# Bounded core harness correctness review

2026-09-09 UTC. Read-only review of the local Responses-only core. Two Important findings, both reproduced using fake backends/environments; no generated code executed, network/model calls, GPU calls, or core edits. These findings concern `src/rlm`, not the separate Prime/nano runtime used by the ongoing root campaign. They must not be attributed to current campaign scores.

## Important: executor output loss disappears from controller observations

`src/rlm/observation.py:38–85` builds the model-visible observation without consuming `ExecutionResult.truncations`. Executor-origin truncation is produced by `src/rlm/executor.py:311–337`; the controller receives the resulting observation through `src/rlm/engine.py:549`.

The reproduction uses the actual bounded output capture: ten characters with a four-character budget produce `stdout="0123"` and an accurate six-character omission record. A fake environment returns that typed result to the real engine without executing the controller's code. The actual next controller request contains the shortened stdout but reports `truncation={"omitted_chars":0,"fields":{}}`, with no executor truncation record. This can make partial tool/context output appear complete. The execution trace still retains the original typed truncation, so this is controller-observation fidelity loss, not destruction of all evidence.

The four-character capture is an intentionally small valid boundary fixture. With default executor and observation caps, a long stdout may also trigger downstream observation truncation, but the executor-origin omissions remain unaccounted for; do not extrapolate this fixture to claim every default truncation reports zero loss.

Suggested focused correction: preserve executor-origin per-channel omissions and distinguish them from any additional observation-level shortening, without double-counting. Retain omission metadata in the delivered observation. No change has been implemented here.

## Important: known usage of a late valid response is omitted from aggregate usage

`src/rlm/engine.py:801–806` checks post-return action/run deadlines before `ledger.record_response`; accumulation occurs in `src/rlm/ledger.py:145` onward. A response object and its usage are already present in the response trace at that point.

A deterministic fake clock advances from zero to two seconds during a backend call under a one-second run deadline. The backend returns a valid Responses object with 11 input and seven output tokens. The expected fatal `deadline_exceeded` occurs, but the aggregate ledger is `{input_tokens:0, output_tokens:0, calls:1, unreported_calls:0}` even though the trace records all 18 tokens. Capped/failed run cost can therefore be understated as complete zero usage.

Suggested focused correction: account for known valid response usage on the late-response path while retaining the fatal deadline outcome and never accepting the late answer. Preserve intentional error precedence for malformed responses/usage; qualify run and action deadlines separately. No change has been implemented here.

## Focused evidence and clean checks

`test_reproductions.py` contains two assertions documenting the current erroneous behavior and two positive checks. All four passed in the stored `CPU_REPRODUCTIONS.xml` run (0.59 s). The bug assertions are evidence fixtures, not desired regression expectations; invert/replace them when fixing.

Positive checks established preservation of full nested unknown request fields, explicit leaf model, subcall role/depth/branch metadata, input-ordered batch responses despite reversed completion order, and input-ordered ordinary batch failure after all outcomes. The bounded inspection found no additional material final-submission fidelity defect. This is not an exhaustive proof of correctness.

Reproduce from this external directory:

```sh
CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/rlm/bin/python -m pytest -q -p no:cacheprovider /project/alex_phd/runs/rlm-research-r4/analyses/core-harness-review-2026-09-09/test_reproductions.py
```

`AUDIT.json` pins the reviewed source and reproduction artifacts. Core worktree was clean when checked. Parent owns any isolated fix worktree and subsequent authorization.
