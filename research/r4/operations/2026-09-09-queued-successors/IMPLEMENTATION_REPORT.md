# Ready for parent acceptance, not launched

The fixed handoff is CPU-qualified: exact root owner exits → accepted anchor service/600-call collection → owned release → empty GPU → indexed SFT. Neither this preparation nor verification launched a GPU process or sent a model request. No shared/frozen source, active experiment, or live queue was changed.

Six focused tests passed on 2026-09-09 (`6 passed in 0.04s`). The initial four desired-behavior tests failed before implementation because the coordinator was absent; they passed after implementation. Added checks cover acceptance/source corruption and service release after startup failure. Ruff passed for all three Python files. A fresh native-Python import verified the frozen suite/lifecycle dependency closure, including the qualified process-title ownership implementation, with no service start.

Checks cover exact prior-owner waiting, PID reuse, predecessor deadline, no launch on occupied GPU or missing acceptance, failed-first → second ordering only after GPU clearance, exact approved input hashes, and finally-based owned release. These are fake-process CPU checks plus read-only dependency authentication, not a new real-service qualification.

Parent must generate/review `coordinator.py acceptance-template`, set `approved` to true, and publish `ACCEPTANCE.json` before successors can launch. The template itself grants no authority. READY records the plan and source identities; the acceptance binds the exact command/input set, which is checked again before each job. The `verify` command only checks path readability and reports whether acceptance exists; it is not a substitute for parent approval or hash validation against approval.

Use the recorded MIG UUID and full LD library path, preserving the inherited local API-key environment without writing it into artifacts. The coordinator never kills the prior root owner, PID replacements, or arbitrary GPU process-list entries. If ownership cleanup fails and GPU workers remain, SFT is not started. No retry or automatic resume is provided. Partial outputs, nonzero exits, and missing completion markers remain visible.

Caps: root's original three-hour deadline plus 120 seconds cleanup; acceptance wait 300 seconds; empty-GPU wait 120 seconds per successor; anchor wrapper 2,400 seconds (collector 1,800); SFT wrapper 5,430 seconds (training 3,600 cumulative, own overall 5,400); owned child signal grace at most 120 seconds. Waiting and actual work have distinct recorded clocks. The existing shared coordinator lease plus a second empty-GPU check prevents overlap with cooperating coordinators; unrelated external launches cannot be controlled by this operation.

Parent reviewed the implementation independently before publication. This operation is intentionally only a two-job serialized handoff. No experiment outcome is inferred from a zero launcher exit or presence of an output marker.
