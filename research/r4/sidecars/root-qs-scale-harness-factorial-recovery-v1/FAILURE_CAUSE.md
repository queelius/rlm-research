# Attempt-001 zero-outcome collector failure and attempt-002 correction

Both attempt-001 root services reached `SERVER_READY`, but their collector processes failed before any
physical request. The retained identical tracebacks enter the qualified `od_collect.implementation()`
and stop at `path=s.JOINT/'collect.py'`: the new study wrapper omitted `JOINT`. Reviewing the complete
transformed collector revealed that its study surface also requires `LABELS`, `corpus`, `load`,
`answer`, and the existing runtime/interface/stack/read/write/authentication members. Its protocol
surface additionally references `error_probe`, `null_row`, and `verify_replay`, even though those
branches are not expected in free readout.

The additive recovery exports the full qualified study surface and composes the missing protocol
members from the exact pinned joint/corrective ancestors. It reuses the original collector and owner
sources by hash. A CPU test calls the actual `od_collect.implementation()`, then enters its real
`run(args)` through a fake HTTP transport; a separate check validates the owner-generated attempt-002
collector argv. All original input files remain byte-identical through a read-only directory link.

The subsequent nonempty prepared-row qualification exposed a second attempt-001 defect before any
GPU relaunch: the task wrapper named its injected setup/finalize argument `runtime_value`, but the
framework calls these hooks by the keyword `runtime`. Recovery V2 supplies the same task package with
the required parameter name and a local stack that uses it. The final CPU qualification runs an actual
prepared 256-record cumulative/free task through `env.run_slot`: two fake root transports, one fake c32
transport, the five setup files, cumulative decoder state, actual 4,096-byte head/tail clipping of a
9,969-byte observation, and the strict scalar `Answer: 148` terminal path all complete. Fake provider
responses mean zero model/GPU calls.

