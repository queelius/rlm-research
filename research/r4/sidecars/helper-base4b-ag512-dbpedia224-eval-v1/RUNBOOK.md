# MAIN-only runbook

Verify the sealed closure, acquire the shared GPU lock, and supply the inherited private credential
only in process memory. Run the exact `READY.json.command` under a 1000-second external cap. Never
retry into `outputs/attempt-001`; any repair or rerun must use an additive attempt/source.

Expected output: `outputs/attempt-001`. A valid completion has 184/184 native calls, 736/736
predictions, `ENGINE_ATTESTATION.json` with the actual batch-invariant kernel marker, and a clean
service release. Analyze against the four existing panel arms without selecting or dropping them.
