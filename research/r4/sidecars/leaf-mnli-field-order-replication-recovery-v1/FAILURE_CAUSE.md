# Attempt-001 prelaunch failure and attempt-002 correction

Attempt 001 produced no scientific request. Its retained launcher traceback terminates while the
replication wrapper loads the qualified new-context wrapper: the outer wrapper aliases `study` to the
leaf replication module, but the qualified wrapper's next seam requires its immediate ancestral study
and accesses `s.ALIEN`. The leaf module has no `ALIEN`, so startup raises `AttributeError` before the
released-base launcher or vLLM subprocess is reached. The owner retained all 96 planned NULL slots and
released the allocation.

Attempt 002 changes only this wrapper namespace seam. It binds the qualified wrapper to
`s.qualified`, the exact immediate study that owns `ALIEN`, then follows the unchanged authenticated
wrapper chain. The 96 plans, requests, contexts, seeds, schemas, scorer, model, caps, and collector are
byte-identical links to the prior seal. A CPU fixture executes the actual wrapper chain through the
real released-base launcher and replaces only its final `subprocess.Popen` and endpoint wait, proving
that namespace resolution reaches the process-launch boundary without GPU work.

