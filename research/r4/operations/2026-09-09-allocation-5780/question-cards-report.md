# Question-card view report

Generated at 2026-09-09T18:19:33Z. This CPU-only documentation task created a lightweight
question-centered view over the sealed research-factory catalog. It did not edit the catalog, its
validation or manifest, any prior report, the research queue, user ideas, repository source, or a
database. It launched no GPU, model, or service work.

## Delivered files

The new [question index](../../questions/README.md) links eight readable cards and one minimal
[template](../../questions/TEMPLATE.md). Each card contains the requested YAML metadata and the same
plain-language sections: question, why it matters, evidence so far, what remains unknown, smallest
discriminating next experiment, and the evidence needed for a stronger claim.

| File | SHA-256 |
|---|---|
| `questions/README.md` | `a99da95e201c52fea0c9ae19f061a0605509196d9eca139f1b0514ca4f853c0a` |
| `questions/TEMPLATE.md` | `d8dc9d43c1ac2e85d4f3ebd7618f09ed1633b4121306e9c628c4ba30b27bd521` |
| `questions/adaptive-communication.md` | `b31defa8a5b88c361ffa4afc5932891a34baea707caa0e2f47616f958579d7d1` |
| `questions/continuation-state.md` | `43e6c921c96fb9e9e0af1f77a35b374953e18aee17ad50efce3c58d4af807d84` |
| `questions/controller-training.md` | `e859220c80a19fbd4ffdaba8207c60f7b80586089f2bafd92f7a203b667aaec7` |
| `questions/correspondence.md` | `0c76a97b39566e93c60e997295b310a8d4a15fef1b6c4c175b2acd834530caa3` |
| `questions/counterfactual-credit.md` | `6cc5c99dbae2a4dc9bb24ccab7b94a836f603cb4dea7d83c4523a51474824509` |
| `questions/executed-reduction.md` | `fc6c09a91db24344752ab16564ab301cf4ff3578aae1c7f05d1c8e191ff14385` |
| `questions/latent-recursion.md` | `8f0edc6f96510a899cf7fb9cfd99d70efeea5c17552e78bc7b91033b94eb36c3` |
| `questions/sufficient-interface.md` | `24293216ec19d0890f5b0aebe2021d9a3882722cbae84016d9a1bc08f46b87c0` |

The authoritative source catalog was rehashed as
`e0fa23412505eee178d27041816e84f7931d6da01b02e13f664393a6586ff39c`, matching its sealed
validation. The later bridge source report rehashed as
`b8b8a05aa748a1a862cd774d6ed6c0f73447aa5f232b425463f4e369181331cb`, and its final manifest
rehashed as `0ea8a5dbb0a80e2ac86f45d33977924f09123e1b049ac913a92029e6cf86ae34`.

## Evidence treatment

Every card preserves the catalog cutoff `2026-09-09T17:32:51.282711+00:00`. The later sealed
teacher-forced cue replay and three-root bridge audit appear under explicitly separate update
sections rather than being folded back into catalog claims. The bridge update retains checksum
0/8, the non-robust across-root count-map effect, and trace evidence of dictionary/container misuse
and missing executed reduction. Deferred questions state that they have no experiment and no result.

At generation time, the first complete-demonstration SFT launch had failed before model use because
an inherited local credential was missing, and a fresh same-input recovery was running. Neither is
treated as an experimental result. This operational observation is not copied into a permanent
positive or negative result claim.

## Verification

A focused Python validation using installed PyYAML 6.0.3 passed. It checked:

- exactly eight cards and exact equality with the catalog's eight stable `rq:` IDs;
- one parseable YAML document per card and all eleven required metadata fields;
- the shared schema version and exact sealed evidence cutoff;
- every claim ID and related-question ID against the catalog;
- the source catalog's path and SHA-256 from every card;
- existence of every metadata report path; and
- all 27 local Markdown link occurrences in the eight cards and index.

The source catalog, later bridge report, and later bridge final-manifest hashes were also checked with
`sha256sum`. No network, model, GPU, database, queue, or historical-artifact mutation was part of
validation.

## Limitations

This is a curated navigation and interpretation layer, not an independent raw audit, systematic
literature review, or complete campaign catalog. It does not add independent replications, resolve
pretraining exposure or dataset licensing, or establish publication readiness. The NeurIPS checklist
is used only for brief reporting principles; no independent detailed review is claimed. Report paths
are intentionally exact and local, so moving the external research tree would require an explicit
migration map or metadata update while retaining stable `rq:` IDs and append-only evidence lineage.

