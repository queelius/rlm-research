# Same512 repeat128 raw audit

Fixed repeated128 versus broader comparison on the same exposed panel; no checkpoint selection.

rl_repeat128_step8: 417 correct /512 planned; 512 available, 0 unavailable; complete=True.
c32: 422 correct /512 planned; 512 available, 0 unavailable; complete=True.
rl_step8: 437 correct /512 planned; 512 available, 0 unavailable; complete=True.

Paired later-arm gains/losses:
c32_vs_rl_repeat128_step8: 2/7, net -5; primary complete=True
rl_step8_vs_rl_repeat128_step8: 3/23, net -20; primary complete=True

All128call clusters and512 planned records retained. Missing is not wrong.
Source-to-raw audit, not independent trainer implementation; class/cost details in JSON.
