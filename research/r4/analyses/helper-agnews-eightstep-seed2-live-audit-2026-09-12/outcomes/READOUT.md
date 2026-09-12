# Same512 seed2 raw audit

Fixed training-seed replication on the same exposed panel; no seed selection.

rl_seed2_step8: 436 correct /512 planned; 512 available, 0 unavailable; complete=True.
c32: 422 correct /512 planned; 512 available, 0 unavailable; complete=True.
rl_step8: 437 correct /512 planned; 512 available, 0 unavailable; complete=True.

Paired later-arm gains/losses:
c32_vs_rl_seed2_step8: 16/2, net 14; primary complete=True
rl_step8_vs_rl_seed2_step8: 0/1, net -1; primary complete=True

All128call clusters and512 planned records retained. Missing is not wrong.
Source-to-raw audit, not independent trainer implementation; class/cost details in JSON.
