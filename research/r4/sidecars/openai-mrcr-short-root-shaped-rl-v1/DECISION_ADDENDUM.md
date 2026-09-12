# Decision amendment after implementation review

The sealed design's final sentence is superseded. A weak or null 16-context heldout result retires
the single LR `1e-5` checkpoint as a positive endpoint; it does **not** retire shaped reward or
forbid a separately prespecified fixed-dose or fresh-training experiment. Such a follow-up may be
motivated by authenticated training mechanics without selecting a checkpoint on heldout quality.

The sealed trainer records pre-update native/HF likelihood agreement, importance weights, replay,
gradient norm, and adapter delta. It does not perform a post-update likelihood sweep, so no
post-update likelihood-shift measurement may be claimed from this run.

The four observed near-success trajectories are not clean evidence of decomposition: they emit
18,683--20,000-character broad tool observations (three are truncated), after which the terminal
model retrieves the target. The shaped reward may therefore reinforce context dumping rather than
correct programmatic selection. Any accuracy gain is a root-procedure signal only; observation-size,
truncation, selected-turn correctness, and tool exceptions must remain interpretation diagnostics.
