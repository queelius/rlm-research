# Erratum: native partition-join audit

This additive correction preserves the original sealed report (SHA
`093887335d59675fcca99fb7f446bf22363c1358207df77e2ebed1737157d56f`) and its manifest.

In “What the extraction stage preserved,” replace the sentence claiming that only world 2's
cross-partition trio was complete for relevant products with: **Four of eight
world/representation packages retained every query-product triple: world 1/co-located, world
2/cross-partition, world 3/co-located, and world 3/cross-partition.** Exact full reports can include
distractors and still preserve all relevant facts; the original diagnostic incorrectly required
equality to the filtered relevant subset and therefore excluded those exact reports.

The other four packages omitted six relevant rows in total: world 0/co-located omitted 1, world
0/cross-partition omitted 1, world 1/cross-partition omitted 1, and world 2/co-located omitted 3.
This is a post-outcome diagnostic only. It does not rescore or repair model outputs, alter the 5/24
exact-versus-19/24 subset extraction result, or change the host-join sufficiency finding of 6/8.
