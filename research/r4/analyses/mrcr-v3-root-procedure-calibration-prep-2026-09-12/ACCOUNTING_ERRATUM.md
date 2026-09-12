# Accounting erratum

The final decision paragraph in `REPORT.md` incorrectly describes the earlier full
MRCR proposal as a “roughly 39-minute training budget.” The frozen proposal's cap was
**3,900 seconds (65 minutes)** and covered collection, an HF phase, and two evaluation
service phases. It was a prospective aggregate cap, not a measurement of the time for
32 MRCR trajectories or for training alone.

This correction does not change the current calibration-only design: its owner cap is
900 seconds, its external supervisor cap is 1,000 seconds, and it performs no optimizer
step.

