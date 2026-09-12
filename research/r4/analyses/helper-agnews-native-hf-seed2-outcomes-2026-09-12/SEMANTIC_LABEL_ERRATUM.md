# Seed2 pairing label erratum

The immutable V1 `REPORT.json` contains the correct predictions and counts, but its
generic pairing helper labels the seed1-to-seed2 regression branch `updated_loss`.
For this comparison, that branch means **seed2 loss**. There is exactly one:
`agtr89afb07a21975481` has gold `Sci/Tech`; c32 and seed2 predict `World`, while
seed1 predicts `Sci/Tech`.

Thus the authenticated outcomes are c32 211/256, seed1 212/256, and seed2
211/256. Seed2 and c32 are prediction-identical on all 256 coordinates. The sole
seed1 improvement did not persist under the prespecified fresh native/HF seeds.
This is an exploratory non-replication on the already research-exposed AG256 panel,
not evidence that broader AG data are unlearnable and not a fresh512 result.

Source V1 `REPORT.json` SHA256:
`fb66be60e7eb45be067b7a6cc7eb11f9a04125ed3671a11202cffea9744e4c0f`.
