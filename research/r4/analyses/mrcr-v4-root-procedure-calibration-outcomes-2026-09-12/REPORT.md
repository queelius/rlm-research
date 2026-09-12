# Independent MRCR V4 calibration audit

Frozen gate eligible: **False**. Decision: `do_not_train_from_this_calibration`. This remains a calibration over eight targets from one research-exposed underlying context.

- Planned/recorded/available: 32/32/0
- Mixed groups / mean score: 0 / None
- Successful/failed `/context.txt` reads: 0/0
- Causal turns reconstructed/usage-matched: 0/0
- Root/child calls: 0/0
- Clean release: True

Official `rfind` scoring and the original prospective gate are recomputed unchanged. A nonempty exception string is not counted as a successful file read. Causal prompt lengths are reconstructed from each sampled node's complete parent chain; isolated sampled-node token lists are not treated as full prompts. These runtime checks are supplementary and do not expand the frozen gate. No optimizer update is authorized here.
