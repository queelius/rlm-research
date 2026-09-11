# Main-only receipt uptake sentinel

This is a new inference-only96-episode sentinel, not a receipt72 rerun or training
job. Main's approved implementation decision is
operations/2026-09-09-continuous-allocation/RECEIPT_UPTAKE_IMPLEMENTATION_DECISION.md.
The complete design is ideas/2026-09-09-receipt-uptake-followup.md. Frozen receipt72
files remain unchanged. This namespace has no scheduler or acceptance mechanism.

CPU preparation uses the existing prime-rl-5990b1b Python, no installs. Own source,
inputs, qualifications and outputs are external to the Git repository. Eight
focused tests cover the exact D→R difference, narrow R→V difference, public-only
setup, actual queue quadruplets,96 seeds/roles/phases, shared runtime deadlines,
owned cleanup ordering, absence observer and unknown outcomes. No broad suite.

Main-only argv after separate source acceptance:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-receipt-uptake-v1/driver.py run --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-receipt-uptake-v1/outputs/attempt-001
```

Main supplies exactly one exclusively assigned CUDA_VISIBLE_DEVICES and the
existing STRICT_RLM_CALIBRATION_API_KEY. Credentials are not serialized. Set
PYTHONDONTWRITEBYTECODE=1. No launch before main approval; no attach to another
process. The owner creates originalA24, step8-48, originalB24 episodes in three
separate fixed-root/c32de services and releases each with the pinned owned
lifecycle. It uses the already accepted disappearing-process observer wrapper,
which treats only FileNotFoundError/ProcessLookupError as absence.

Work deadline is run start+3480s; inclusive owned deadline start+3600s; outer
operation timeout3630s. Cumulative collection2400s is shared across phases with
600/1200/600 phase limits. Collection subprocess elapsed, including its CPU startup,
is charged against the cumulative ledger. The final collection may have less than
600s if earlier subprocess grace was consumed. No deadline reset, automatic
episode retry, implicit output reuse, or checkpoint selection. Incomplete/capped
phases stop the study and preserve all retained artifacts and unknown coordinates.
The shared allocation deadline remains authoritative.

Inspect TERMINAL.json, each phase rollout/STATUS.json and owned SERVICE_STOPPED.json.
Actual runtime source binding, provider tokens and role request IDs are retained.
Output containers and service processes are only those created by this invocation.
There is no in-lock CPU analysis after release. To project afterward, explicitly run:

```text
/project/alex_phd/envs/prime-rl-5990b1b/bin/python /project/alex_phd/runs/rlm-research-r4/sidecars/root-receipt-uptake-v1/driver.py analyze --output /project/alex_phd/runs/rlm-research-r4/sidecars/root-receipt-uptake-v1/outputs/attempt-001
```

The projection is descriptive, not an independent final audit. It retains all
physical terminal-attempt records and request-only unknowns. Primary uptake is
an embedded helper request plus source validation and native child corroboration,
not a count of matching model turns mislabeled as API calls. Root-writable receipt
access claims and structural map validity do not establish semantic truth or
causal incorporation. Final strict score and native usage remain separate.
