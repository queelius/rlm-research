# MAIN runbook

MAIN owns acceptance, the exclusive GPU lock, launch, termination and successor handoff. Before
either command, privately bind the already approved local provider credential as nonempty
`STRICT_RLM_CALIBRATION_API_KEY`; never put its value in an artifact or argv.

Verify with the exact `verify_argv` in `READY.json`. Launch only the exact `argv` in `READY.json`
after confirming `outputs/attempt-001` is absent and the accepted predecessor has released its owned
service. The single shared envelope is 1,800 seconds: 1,680 seconds for startup and collection,
1,770 seconds inclusive ownership, and 30 seconds for the outer parent. There is no automatic retry.

Success requires the owned terminal and collector status, all 96 coordinate records, preserved raw
responses/native token IDs/usage, and authenticated service release. A partial or failed run remains
evidence with unrun coordinates and NULL bounds; do not reroll inputs or repair outputs.

