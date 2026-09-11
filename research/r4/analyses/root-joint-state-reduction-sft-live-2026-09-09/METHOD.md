# Independent joint-state SFT audit method

Timing: frozen after the 21:39:16 UTC launch and after teacher/controlled capture, gate, and joint
training had completed; reduction-stop training was active. No readout outcome had been exposed to
MAIN or read by this auditor. The auditor had been told that the gate passed with projected joint
180.4 seconds/control 72.9 seconds and that two joint checkpoints existed at 21:50. This is an
independent prospective readout audit but not an outcome-blind audit of capture, gate, or training.

Primary question: does the trained free policy actually execute acquisition, retain/merge live child
maps, perform the requested user/category reduction, and stop with exact `Answer: N`? Strict gold
success and operational availability are primary outcomes. Loss, scalar agreement, map literals,
and code mentions are diagnostics and never prove execution.

Audit all 72 heldout coordinates and separately label 12 training-state diagnostics. Preserve the
three policies (unchanged, joint4, reduction-stop4), free versus controlled continuation, width,
scope, alias, and four exposed heldout context clusters. Alias and width are confounded by design;
joint/control have unequal target tokens, reduction mass, and FLOPs. No endpoint-count inflation.

Authenticate native root/child identities, prompt and completion tokens, final envelope, usage,
finish route, and source-replay equality. Returned malformed/tool/capped policy output is zero;
missing/unreturned/native-inconsistent endpoints are NULL. Audit executed final-branch programs and
tool returns for genuine child acquisition, per-call strict maps, accumulation/update versus last
overwrite, scope/count, and exact stop. Never execute model programs, reorder, repair, or infer use
from a matching scalar.

Audit training lineage, masks, role weights, corpus coverage, gate arithmetic, fixed checkpoint-4
selection, actual Adam updates, target tokens/FLOPs, elapsed stages, and checkpoint/optimizer hashes.
Separate 60 physical teacher/source child acquisitions (40 train, 20 controlled) from source replay,
hypothetical standalone costs, and new readout calls.
