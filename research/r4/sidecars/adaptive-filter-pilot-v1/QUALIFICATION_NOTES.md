# CPU qualification history

All listed provider tokens/logprobs are deterministic fixtures, not model
observations, behavior likelihood evidence or training examples. Actual model/GPU
calls: zero. Only newly owned rootless runtimes and a local CPU fixture provider
were used; active/frozen sidecars and research services were not changed.

- Contract tests first failed because the new module was absent, then passed
  strict object validation and request independence from synthetic user metadata.
- Planner/collector/setup tests first failed on absent implementations. One test
  initially resolved an older results module on the inherited import path; its
  existence check was made local before using the new module.
- Qualification001 passed operator-valid/free-valid/operator-invalid. It used
  inherited300/900/60/60 episode timeouts and initially exposed the operator
  program to free. Preserved as superseded evidence, not the final qualification.
- Qualification002 failed before provider calls: a timeout was assigned to
  ModelContext, which carries model/client/sampling only. Source inspection showed
  timeout belongs to SingleAgentEnvConfig.agent. This was fixed at that typed seam.
- Qualification003 passed with45/300/15/15 and native operator/child ancestry.
  Its free runtime still contained the operator program: superseded by review.
- The setup-surface regression then failed explicitly on the leaked operator
  program/config. Only operator arms now get those files. The corrected test
  passes; common public files remain byte-identical across arms.
- Qualification004 passed on corrected surfaces. The free fixture asserts inside
  IPython that no operator_program.py or operator_config.json exists; its initial
  child tokens/sampling match the operator's exactly.
- Qualification005 is the final acceptance proof: corrected surfaces, full native
  initial-child identity, nullable spawning-request ancestry, invalid-map handling,
  plus a user-filter fixture verifying the irrelevant user's record is absent from
  the child request and the computed count is returned through ACP.
- qualification-cancel-attempt-001 passes one pending operator-child cancellation:
  zero root requests, one native child error attempt retained, no terminal count,
  and ordinary environment-serving cleanup exits. Operator setup bytes were not
  changed by the later free-only file-surface correction.

Input preparation initially computed the remaining-set hash with compact JSON,
whereas the inventory uses newline-joined sorted IDs; the actual1454 membership
was identical. The96 SST2 curriculum groups were also distinguished from the3040
TREC groups. Corrected inventory conventions before publishing input files.
The actual child-role-suffix catalogue was located afterward; all four contexts
are already excluded curriculum contexts, documented additively without any
reallocation. Public512 membership and user/global answer skew were not changed.

The inherited raw correctness scorer reports0 for an empty operator failure;
the declared audit projection preserves that raw value and separately reports a
null unanswered endpoint. No stored scientific reward schema is rewritten.

Final focused test stdout, stderr, exact argv and elapsed time are in
FOCUSED_TESTS.json. Runtime overlays and all fixture provider requests are retained.
READY is written only after final proof, source checks, focused tests and compile.

The first freeze attempt wrote exact REQUESTS, CANONICAL_REQUESTS and SEED_AUDIT,
then failed before publishing SPEC: Prime typed environment validation mutates its
input nested dictionaries, leaving an RLMHarnessConfig not JSON serializable.
Validation now receives a deep copy. The explicit second CPU freeze invocation
reuses those three files only on exact parsed-content equality, never overwrites
them, and does not retry any episode. No READY existed at the failure.
