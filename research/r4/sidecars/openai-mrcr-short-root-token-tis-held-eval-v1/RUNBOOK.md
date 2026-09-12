# Runbook

Run the three READY stage commands sequentially under the established shared GPU lock, each
with a 700-second external cap. Owners wait for and authenticate the completed two-branch
trainer before starting a service; they refuse partial training, a selected branch, changed
held inputs, or an existing output. MAIN owns all launches and private credential injection.

The intended fixed order is `base`, `lr1e-5`, `lr1e-4`. A model-level unavailable answer is
preserved and does not authorize changing the panel or choosing a different checkpoint.
