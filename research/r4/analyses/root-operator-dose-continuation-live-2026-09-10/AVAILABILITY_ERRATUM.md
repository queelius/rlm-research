# Additive availability arithmetic erratum

The sealed `REPORT.md` availability paragraph and the separately frozen intermediate-readout design
motivation say the fixed6/fixed24 readout had 23 NULL slots among 96 planned endpoints. That sum is
wrong: fixed6 had 31/48 native finals (17 NULL), and fixed24 had 38/48 native finals (10 NULL), so
the total is **27 NULL slots**, not 23.

Pairwise accounting is consistent with that correction: 27/48 coordinate pairs have both native
finals; among the other 21 pairs, 4 have fixed6 only, 11 have fixed24 only, and 6 have neither.
Thus fixed6 availability is 27 + 4 = 31 and fixed24 availability is 27 + 11 = 38.

This changes no native-final classification, score, pairwise comparison, or bound. The reported
strict scores (fixed6 5, fixed24 29) and bounds (5--22 and 29--39) remain correct. This erratum is
additive and does not alter the sealed report, design note, audit JSON, plot, or earlier manifests.
