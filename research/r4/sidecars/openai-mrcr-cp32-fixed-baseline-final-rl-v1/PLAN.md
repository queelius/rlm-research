# Fixed-baseline final-decision REINFORCE implementation plan

Goal: one genuine reward-weighted terminal-decision update from exact cp32 and the completed32 native trajectories, with fixed b=.5 instead of a within-group baseline.

Architecture: reuse the admitted token-TIS scoring, replay, RNG and fresh-Adam helpers. A small input adapter authenticates the current32 bare finals and records all other root actions as zero-loss. One explicit trainer loads cp32 once, accumulates the fixed objective, saves qualification/gradient-localization receipts, then takes at most one step. MAIN alone may launch after reviewing READY.

Global constraints: all8G4 groups/32 trajectories retained; denominator32; advantages raw_exact-.5; T=.5; detached token-TIS cap2, deliberately biased and never mislabeled exact sequence IS; no >=2-mixed gate, no unlikelihood loss, no gold-token substitution; only actual bare final action tokens including EOS carry loss; unchanged root-prefix/native/stop/hash checks; fresh AdamW LR1e-5, weight_decay0, clip1; cp32 initial tensors; science900/owner1100/external1200 seconds; held/long data never in gradients; no GPU authority here.

1. Implementation + focused CPU qualification: create study.py, core.py, inputs.py, train.py, owner.py, prepare.py and two focused tests. Exercise actual loss signs/denominator/final masks and a tiny actual HF/PEFT replay/no-step-failure/update. Record initial tensor and source bindings, selected HF logps and negative-group body/whitespace/EOS gradient contributions without changing their summed objective.
2. MAIN review/admission: freeze source+data+CPU receipts and exact argv. No automatic launch or optimizer admission follows preparation. Both fixed held and long evaluations are separate conditional successors, with the unchanged cp32 baseline and no endpoint selection.

