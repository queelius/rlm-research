# Broader AG eight-step answer-only SFT control

This conditional, exploratory arm starts from exact c32 and makes eight ordinary
full-vocabulary answer-only SFT updates on the frozen eight disjoint AG steps. Each
update consumes 32 gold B4 JSON maps (128 unique records). The optimizer is fresh
at step zero and carried across steps; checkpoint8 is the only endpoint.

This is a data-signal positive control, not a pure SFT-versus-RL comparison: the
RL arm uses four sampled maps per group, grammar-masked support, reward contrast,
and importance weighting. No heldout record is loaded here and no intermediate
checkpoint is selected. The shared fresh512 evaluator may bind only through
`sft_study.endpoint()` after all eight commits and the owner terminal authenticate.

MAIN alone may run the exact READY command under the shared GPU lock and an
external 1000-second cap. A timeout or partial checkpoint is preserved but is not
eligible for the fixed endpoint.
