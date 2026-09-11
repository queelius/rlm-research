# Accumulation ledger implementation plan

Goal: prepare the approved global16 inference comparison, without training or GPU calls.

Architecture: new isolated sidecar reuses pinned native free-root tasks, typed-child source matching, capture and owned service lifecycle. A study-owned runtime overlay stages valid child maps and commits only successfully delivered broker results; root observations append a deterministic snapshot after existing truncation. Shadow audit runs in both arms.

Tech stack: existing native Python, nano4ef engine/supervisor, Prime native client, immutable local preinstalled image. Spec: DESIGN.md plus referenced approved design; MAIN_APPROVAL.md overrides provisional truncation wording.

1. Write focused tests first in test_ledger.py: repeated equal IDs deduplicate; conflicts remain visible/excluded; exact ID/text rejection and episode/root isolation. Capture the expected missing-module RED result, then implement ledger.py public source-only state/request matching. Test pending versus successful delivery and original answer preservation at the integration seam.
2. Inspect and pin actual supervisor delivery and engine truncation/logging source. Implement adapter.py / overlay.py using counted source transforms only in owned copies. Truncate unchanged original text, append bounded summary only at depth0, log and capture honest final observation; keep separate raw tool content. No broad framework or broker schema changes.
3. Implement study.py / collect.py / driver.py over qualified native collection and lifecycle. Freeze four exact named contexts,16 coordinate IDs, seed collision evidence, fixed weights and image. Pairs run sequentially, at most four units concurrently. No retries or substitute episodes. Absolute collection/work/owned deadlines1200/1650/1770 and outer1800.
4. Run one scoped CPU-only fake-native rootless fixture for the three cases and actual root prompt/graph/child-answer binding. Preserve all failures and evidence; no live model or GPU call. If narrow source seam fails, report rather than silently widen it.
5. Publish SPEC/inputs/provenance, focused test evidence and RUNBOOK. Verify exact small source closure and original-v-treatment initial input equality; READY written last. MAIN reviews and launches separately. Outcome audit is prospective and all16 denominators remain, including NULLs.

No subagents, broad tests, installation, image rebuild, accepted-source edits or host execution of sampled model code. External sidecar is the requested isolation boundary; no repository commit/merge.
