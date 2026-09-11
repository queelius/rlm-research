# CPU implementation boundary

Approved DESIGN and PLAN remain byte-identical. New files only: study/train/readout/launch/prepare, focused tests, immutable inputs and this handoff. No original or live source changed.

Native tests exercise the real private original collector/lifecycle import composition and actual native CPU rendering of all24 prompts. Training tests exercise unequal-length scalar weighting, shifted action masks, four tiny real LoRA optimizer steps, unchanged frozen base and adapter/Adam/RNG/cursor persistence. Tiny synthetic model parameters and authored fixture values are not training data or behavior likelihoods.

The test-only loader initially used an alias while inherited native loading prepended an old source directory. Later tests then resolved old study.py. The real CLI imports the new canonical study module first. The fixture now does the same; no runtime namespace or inherited source workaround was added for that test issue. A deliberately changed prepared prefix failed before its readout-composition guard was implemented. Initial missing-wrapper RED failures are retained in the tool history.

Qualified source verification is cached per process, not repeated inside an episode; live process ownership checks remain dynamic. A private cache of the immutable historical task prototype only avoids rebuilding identical CPU metadata for every frozen prompt. The original task constructor copies the prototype before assigning public context, prompt, gold and source metadata. It does not cache model output or change the task content.

READY publication means the CPU source/input checks passed. It is not acceptance, a live smoke result, an accuracy claim or permission to expand training data/grammar/prompt scope. MAIN reads and binds the source before launch; terminal outcome analysis is separate and outside GPU ownership.
