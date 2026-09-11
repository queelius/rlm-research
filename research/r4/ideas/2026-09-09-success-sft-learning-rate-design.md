# Stronger update on the same complete trajectories

MAIN design decision, September9,2026,14:35UTC. Exploratory optimization-strength
test, not a confirmatory learning-rate sweep. The independent initial72-case
readout gives baseline5/24, complete-success SFT8 9/24 and last-savedRL7 9/24.
These are exposed contexts. The new comparison is motivated by that signal and
must say so; its fresh paired sampling seeds are not new source holdouts.

## Options and decision

A: Continue24 more complete passes from SFT8 with continued Adam. This tests
training dose but costs roughly another30minutes before readout and can overfit
the same27 trajectories.
B: Repeat the same8 full passes from the same efab start/fresh Adam with LR1e-4
instead of2e-5. This is the narrowest fast test of whether the small successful
SFT update was too conservative. Prefer B now.
C: Add diverse demonstrations instead. This may address copying more directly,
but needs a new data-quality and provenance decision; prepare later rather than
silently alter this fixed-corpus comparison.

Approve CPU preparation of B and a48-episode paired readout. GPU launch requires
MAIN's exact-source READY review and owned coordinator acceptance. It is a new
sidecar, never a rerun or hot edit of the completed study.

## Fixed scientific contract

Same exact27 confirmed training-only episodes,114 physical root turns,
15,256targets/pass, all recovery turns, native prefixes/action masks/recorded stops;
no retokenization/repair/new training data or child credit. Same starting
efab2913 SFTfinal4, fresh AdamW, BF16 base/FP32rank8 adapter, no dropout,
equalepisode→equalturn→mean physical action CE, eight complete corpus passes.
Training seed981308002 and all eight episode orders are intentionally shared
with the low-LR control. The sole declared numerical training change is LR1e-4.
Do not characterize coefficient masses as gradient shares.

Control is existing complete-success SFTfixed8 adapter
66cce4009628ff7d8e047f08e6fb3a29febdbf8fb3ed8303871f69860f1151d5,
selected by fixed update count, not its9/24 result. High-LR arm is new fixed8.
Save each update's real adapter/Adam/RNG/cursor/source identity and record finite
gradient, delta, weightedCE/tokenNLL, actual coefficients and full122,048target
exposures. No old optimizer imported; no resumed learning-rate change masquerades
as the same run. Existing shared environments/base/runtime/child remain unchanged.

Both arms run the same24 exposure-declared validation/query/length coordinates,
eight each, fixed childc32, actual local native tool interface/prompts/caps.
Fresh evaluation seed namespace981314: master981314001; validation101–108,
query201–208,length301–308. Bounded collision check; shared training seed is
explicitly exempt because paired order is intended. Freeze phase order by
SHA256(master:arm) before new inference. Primary high-minus-low strict Answer:N
paired correctness; format, coverage, literal-helper copying, map-to-count and
all physical costs separate. Invalid completed replies0, unavailableNULL, no
repair or pooling old outcomes. High-vs-low isolates this paired recipe change,
not a general optimal learning rate or efficiency gain.

One GPU serial training/services; proposed3330outer/3300owned/3180sharedwork,
1200trainingprocess and900percollection, startup and cleanup consume shared
clock. Native/input/test qualification CPU-only. Use thin private authenticated
adapters over the qualified complete-success trainer/readout/lifecycle; no broad
framework refactor, tokenizer conversion or historical artifact changes.
Standalone source reuse must count/assert any learning-rate and identity seams.
