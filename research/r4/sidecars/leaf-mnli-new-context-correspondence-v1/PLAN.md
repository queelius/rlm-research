# MAIN-approved CPU implementation

MAIN approved the complete design b5c6cfc1… and YAML1490d1aa… on2026-09-10. Their earlier design-pending wording is historical, not a current authority ambiguity. No GPU/service/lock/queue authority is granted here.

1. Retain selected input bytes402f5597… and corrected FEASIBILITY_V2 receipt0b32e370…; preserve invalidV1 prefix receipt. Byte-copy the frozen input into DATA.json and pin its origin, public source/license and explicit MNLI exposure inventories. No reselection/gold balancing/context expansion.
2. Use a unique mn_study/mn_protocol/mn_scoring namespace and explicit aliases only at pinned inherited runtime seams. Reuse exact32 request preamble/sampling/schema; replace shift17 with a common constant and replace8×2 contexts/seeds with16×1.
3. Generate all32 requests/ordered bodies and actual native prompt IDs using the qualified typed vLLM request. Verify8192 context/3072 allowance, schema/gold independence, every canonical label at every position and wrong-tag rejection. Constant duplicates are intentionally legal.
4. Reuse the qualified checkpointed32 collector and released-base owner/service. Preserve REQUEST/RESPONSE/RESULT separately, no automatic retry or reusing an attempt. Additive raw-response recovery is analysis-only; do not add a resumable scheduler.
5. Focused CPU tests exercise actual collector32 transport/token authentication, malformed/tool0 versus NULL, expired-clock planned inventory, actual owner→collector/service→config→intercepted Popen, exact source boundary and input selection/masks. No model load/generation.
6. Seal source/input/CPU closure as READY for MAIN acceptance; exact new namespace and1200outer/1080work/1170owned. Report paths, source deltas, tests and known token/diversity/exposure limitations.
