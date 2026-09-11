# Additive accounting erratum

The sealed `REPORT.md` calls three SFT6 and six SFT24 no-RESULT slots “unrun.” That wording is wrong.
All nine episodes were attempted and retain physical request records plus `FAILURE.json`; none has an
authenticated final, so every slot remains NULL and all correctness, pairing, and bounds are
unchanged.

The three SFT6 episodes contain 5, 19, and 12 root request records. The six SFT24 episodes contain
38, 23, 27, 27, 18, and 14 physical records. Each episode's last recorded provider request returned
HTTP 400, and each retained episode failure is a `TimeoutError` after 181.09--182.76 seconds. These
are attempted collector-exception episodes with no RESULT, not unrun inventory.

The six SFT24 no-RESULT directories contain 22 child calls (15, 1, 1, 1, 2, and 2). This reconciles
the interim 53 child calls counted only in RESULT-bearing rows with the final physical ledger's 75:
53 + 22 = 75. It also makes the statement that SFT24 attempted child acquisition in 48/48 planned
endpoints internally consistent. Physical attempts without an authenticated final do not become
scored model outputs.

This erratum is additive. It does not alter the sealed report, audit JSON, plot, or original final
manifest.
