---
title: Fresh-context positional-anchor192 report denominator erratum
date: 2026-09-10
status: additive_correction
---

The sealed report incorrectly says each cell's early and late segments each contain 384
labels. Each cell has 16 calls: positions 1–16 contain **256** labels and positions 17–48
contain **512** labels. The table's integer counts, the audit JSON, and every reported primary
and relation-specific denominator already use the correct 512-label late segment.

Therefore no score, effect, gate, or interpretation changes: the primary remains
`657 / (16 contexts * 3 relations * 32 late positions) = 657/1536 = 42.7734375` percentage
points, and the present-row relation effects remain +235/512, +242/512, and +237/512.

This erratum preserves the original report at SHA-256
`2e0599eb47f2e8bbb73e8ddf7c504763798d089b5e2f507a35696ad1bf9684e5` and its original
final seal at SHA-256
`49f0f7b6160af37849214350a4cc36a50822c3e96716c9f5e7282078e2e78d17`.
