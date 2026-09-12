# Independent source-to-raw RLOO readout and saved-gradient analysis

Reuse the frozen reviewed paired native decoder, exact official scorer and causal-map helpers through explicit private phase/checkpoint bindings. Primary: RLOO versus cp32 on 32 new-seed held outputs. Secondary same-short comparison versus fixed-baseline RL; long16/fourneedle16 versus cp32. Retain 16 context units per panel, unknowns, physical starts/results/orphans and measured costs. No new score definitions, model calls, generated-code execution or outcomes-based selection.

The saved-gradient analysis checks actual source masks and state hashes, rescales negative preclip components to the saved postclip gradient, and computes a positive-gradient residual. It separates gradient-vector accounting from nonlinear Adam parameter updates. Positive token subcomponents were not saved separately, so they cannot be retrospectively identified as whitespace/EOS/body without new backprop. No such backprop or optimizer execution is authorized here.

Files: analyze.py is thin explicit binding/build/report glue; gradient.py computes saved-vector/token-inventory diagnostics; test_analyze.py exercises a real new-seed cp32 raw control and hand-derived clipping accounting; prepare.py freezes CPU_READY. Make exactly one completion check after sealing; MAIN may invoke another fixed output later.
