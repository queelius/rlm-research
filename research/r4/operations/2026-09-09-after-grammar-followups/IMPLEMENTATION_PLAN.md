# After-grammar controls Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Automatically run the accepted B80 companion and padding128 after the exact grammar160 coordinator exits.

**Architecture:** Import the existing frozen coordinator, rebind only its operation ROOT, and retain its shared GPU lock and owned-process lifecycle. A static PLAN binds immutable inputs, exact commands, predecessor identity and complete deadline; main publishes acceptance only after source review and focused checks.

**Tech Stack:** Existing Python 3.12 environment and qualified Python coordinator; no package installation or live environment mutation.

**Spec:** `../2026-09-09-proceed/B_CONTROL_BRIEF.md` and `../2026-09-09-proceed/PADDING_CONTROL_BRIEF.md` specify the two independent exploratory studies. This plan implements their serialized launch, not their experiment logic.

## Global Constraints

- One exclusively reserved A100; never overlap services or signal a predecessor.
- Preserve the accepted grammar160 sources, plan and outputs unchanged.
- B80 first, padding128 second; independent failures remain visible and are never retried automatically.
- Each child has a 900-second collection cap. Padding's 1800-second owned clock starts at main entry; B's starts inside execute after source verification. The outer process cap is 1830 seconds, plus the unchanged coordinator's bounded owned-child signal grace if necessary.
- B uses this operation's `B80-owned`; padding uses its sidecar's `owned/attempt-001`. The wrappers and parent refuse existing output/attempt paths.
- Parent source acceptance is required; CPU preparation is not launch authority.
- External research-store placement follows the user's research layout. No Git commit or push is implied for this operation.

## Task 1: Bind the unchanged runner to this operation

**Files:** Create `test_handoff.py`, `handoff.py`, `PLAN.json`, `OWNERSHIP_EVIDENCE.json`, `ACCEPTANCE.json` and `RUNBOOK.md` here. No predecessor or sidecar source is modified.

**Interfaces:** Consume `load_coordinator().main()` and the unchanged coordinator PLAN/acceptance schema. Produce `handoff.py run`, which executes the two exact accepted child commands after the predecessor exits. The shared lock remains `sidecars/root-rlvr-campaign-v1/COORDINATOR.lock`.

- [x] Write and run the focused loader test before adding the loader. Observed all three fail with missing `handoff.py`.

```python
def test_only_root_is_rebound():
    op = load_wrapper().load_coordinator()
    assert op.ROOT == ROOT
    assert op.LOCK == ROOT.parents[1] / "sidecars/root-rlvr-campaign-v1/COORDINATOR.lock"
```

- [x] Add the minimal source-authenticating loader below. Reuse, rather than copy or alter, the scheduler implementation.

```python
import hashlib
import importlib.util
from pathlib import Path
ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "2026-09-09-queued-successors/coordinator.py"
SOURCE_SHA = "7d3294241939297741f26ca657782f757e43b520a717a17a6edac378f32873c1"
def load_coordinator():
    if hashlib.sha256(SOURCE.read_bytes()).hexdigest() != SOURCE_SHA:
        raise ValueError("qualified coordinator changed")
    spec = importlib.util.spec_from_file_location("after_grammar_controls_coordinator", SOURCE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.ROOT = ROOT
    return module
if __name__ == "__main__":
    load_coordinator().main()
```

- [x] Run `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /project/alex_phd/envs/prime-rl-5990b1b/bin/python -m pytest -q -p no:cacheprovider test_handoff.py`; observed all three shared-lock/source-authentication/owner-identity tests pass in0.03s. No broad suite.
- [ ] After B80 is CPU ready and parent-reviewed, construct static PLAN with jobs B80 then padding128. Bind each sidecar SPEC and READY source closure, weights, exact owned command and terminal markers, together with this operation's loader/test/runbook and the qualified coordinator.
- [ ] Authenticate grammar predecessor PID2129741/start1072915615, its START/PLAN/ACCEPTANCE and same-user process identity. The conservative predecessor deadline is1788935662.2401078: upstream1788932092.2401078 plus120+300+120+2730+120+180 seconds. This is an upper bound, not a scheduled start delay.
- [ ] Generate source hashes and acceptance through stdout and apply_patch, validate with `op.validate_acceptance(value, plan)`, and retain checks in the runbook. Never auto-approve a template produced by an agent.
- [ ] Launch `handoff.py run` using only the owned predecessor's allowlisted environment; do not print credentials. Confirm its exact PID/start and waiting event, and update the live research queue and session handoff.

Main executes inline under the already selected executing-plans workflow. The user has explicitly delegated decisions and asked for no blocking approval questions. A separate implementation-choice question would therefore be inappropriate. Focused review and acceptance are internal checks, not requests to the user.
