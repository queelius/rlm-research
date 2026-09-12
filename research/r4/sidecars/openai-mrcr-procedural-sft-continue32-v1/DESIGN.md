# Fixed procedural-SFT continuation to total32 updates

Question: does extending the unchanged authored procedure dose beyond four updates make the
model execute the procedure on its training panel? The first readout failed acquisition:
zero raw exact among 28 available/32 recorded, invented JSON schemas, and no teacher-style
successor retrieval. All32 teachers and initial native prefixes were independently checked.
See analyses/openai-mrcr-procedural-sft-first-readout-2026-09-12 in this research store.

This additive owner restores the immutable original checkpoint-0004 adapter, its complete
AdamW state (504 parameter slots, absolute step4), and Python/NumPy/Torch CPU/CUDA RNG.
It performs absolute steps5..32, with the original per-step shuffle seed, frozen32 teacher
episodes, exact suffix masks, per-example token-mean CE, action weight1, terminal weight0.1,
LR1e-4, and weight decay0. The existing source objective and checkpoint writer are reused.
All504 loaded FP32 LoRA tensors and every saved optimizer slot are checked before work.
Only root LoRA parameters are trainable. No model generation or held data is involved.

Checkpoint each update. The first new commit links to original checkpoint4; later commits
link to their immediately preceding step. Adapter/optimizer/RNG/state/binding files have
the original commit schema. The fixed primary is checkpoint-0032, regardless of loss.
The original failed dose and evaluation remain untouched. An interruption preserves all
completed commits; any further continuation must use a separate admitted owner.

The proposed owner cap is1500 seconds, with a1600-second external cap and one assigned GPU.
The prior four-step owner took160.7 seconds; a linear28-update extrapolation is1125 seconds,
including checkpoint overhead in that conservative estimate. These are planning estimates,
not a promise. MAIN alone admits and launches. The new evaluator uses the same train32
manipulation gate; held readout is conditional on passing it and is still exploratory.

CPU verification materializes only saved LoRA tensors over the real Qwen module hierarchy
on a metadata-only base. It checks actual Adam/RNG restoration, a controlled continued step
against an independently restored reference, tampered-adapter rejection, and the actual
inherited checkpoint binding. It does not claim GPU forward/backward or CUDA replay.
