# Fresh16 one-shot audit

`analyze.py run --output <new-directory>` verifies CPU_READY, makes one terminal check, and either writes PENDING/HOLD or invokes the unchanged corrected native auditor with explicit fresh SIDE/ATTEMPT/READY bindings. No polling/model/GPU calls. Run only after MAIN reports completion; do not overwrite an outcome directory.

Native audit verifies the exact frozen prompts/request IDs and checkpoint chat-template prefixes, checkpoint/no-LoRA/runtime dispatch/release, canonical versus raw response hashes, completion IDs/text, independent strict scalar/DSL output values, supplied targets and all32 call costs. It checks the fresh sidecar closure once after terminal. Original code/interpreter/metrics are not modified. Every16-case within-panel direct/DSL pair is retained; unknown is not a loss. RESULT.json references raw-proof artifact hashes.

Old16 outcomes are a separately labeled descriptive block, never matched to new pages or pooled as64 independent questions. Source-question/annotation errors remain limitations, not filters or repaired targets. Keep malformed programs, wrong source operands, wrong arithmetic/scale and unknowns distinct in manual case inspection after terminal. The frozen demonstrations are not model-weight learning; no new prompt variant or follow-up is authorized here.
