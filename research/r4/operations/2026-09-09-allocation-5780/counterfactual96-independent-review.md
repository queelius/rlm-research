---
schema: counterfactual96-independent-review-v1
reviewer: question_cards
reviewed_utc: 2026-09-10T10:16:00Z
status: no_material_issue_found
ready_sha256: cc4067934f518f98477fcfda50a185dc9e892e0f87cde644540ac39083d2be22
identity: 7e3da8c1ce229f530356b95c72af125ef0b0b1b4677709f8c6c0a5b3c0cbf040
---

# Independent counterfactual-card96 review

I did not author this sidecar. I read its final design and all new Python/test sources, then independently ran the sealed owner verifier and recomputed all 5,530 READY source/input hashes. Both checks passed. MAIN had already rerun the ten focused tests; I did not duplicate the four comparatively expensive authored-native fixtures.

The immutable inventory is 96 rows: 24 each in original-U, original-P, counterfactual-U and counterfactual-P. Each of 24 source blocks shares one fresh seed across its four cells, and each cyclic dispatch order occurs six times. The seed and native-context collision receipts are empty. The selected GATE hash is `ce10e939b210bcc11c14d47cdf27a2ab57799146f9c1670f503bb006b9c16880`; the card hash is `c4afc11d1e1aa16e2cf5ca8809ea4e97e5e9ca883bbde75dcd6cb4c7ed165e59`.

The source preserves exact original-U native prefixes and files, makes U/P task files identical within each variant, mirrors counterfactual weights in both record representations, and scores the row's actual threshold. The 3,600/3,570/3,450-second outer/owned/work clocks leave 120 seconds for qualified release and 30 seconds for final harvest; all missing or unauthenticated native finals remain NULL in the planned inventory. The counterfactual availability gate is directionally defined only for P versus U; original availability remains separately reported.

No material source, input, binding, ordering, NULL, cap or cleanup issue was found. This is an exposed, gold-conditioned diagnostic intervention and not fresh-context or primitive-preservation evidence, as the design states.
