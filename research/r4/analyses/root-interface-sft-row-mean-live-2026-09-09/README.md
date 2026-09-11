# Equal-row SFT: independent readout audit

Status: **method and parser prepared; awaiting MAIN's terminal trigger. No new outcomes read.**

[METHOD.md](METHOD.md) freezes the comparison and interpretation rules. [EXPECTED_INPUTS.json](../../../../ARTIFACTS.md#unpublished-files "Not published: EXPECTED_INPUTS.json") records the independently checked 32 training rows, four ordered batches and 24 paired fresh-seed coordinates. [audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: audit.py") reconstructs training identities, native inputs, strict outcomes, helper coverage and physical token costs; [test_audit.py](../../../../ARTIFACTS.md#unpublished-files "Not published: test_audit.py") provides five focused CPU fixtures.

R is the new equal-row fixed-four-update checkpoint; T is the existing token-normalized fixed-four-update checkpoint. Both start from the same historical root with fresh Adam and retain the same typed child interface. Objective coefficient mass is not measured gradient share. Completed invalid replies are failures; unavailable/incomplete trajectories remain null. No RL training-admission gate is added to this endpoint comparison.

After the explicit terminal trigger, the native CPU interpreter runs `audit.py audit --main-terminal-trigger`. This directory will receive an additive result report and metric/source manifests. Preparation does not poll the experiment or control any GPU process.
