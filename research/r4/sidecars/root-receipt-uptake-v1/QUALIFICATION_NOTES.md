# CPU-only qualification attempts

Attempt001 retained three deterministic fake-provider calls and one complete
unchanged original-root fixture. The exact offered snippet executed successfully,
and the pinned exporter authenticated its root-child-root native chain. The new
diagnostic then failed because it assumed an ACP request ID equals a role-audit
filename. Frozen root_export.py lines75–81 instead indexes each file's explicit
request_id field. Added an adversarial filename/field regression test, watched it
fail, and adopted that exact qualified identity mapping. No runtime/helper/model
behavior changed. Attempt002 is an explicit new CPU-only qualification, not an
inference retry; all attempt001 files remain unchanged. No model calls occurred.
