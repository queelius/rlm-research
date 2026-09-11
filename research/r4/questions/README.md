# Research questions

This directory is a question-centered reading view over the sealed [research evidence
catalog](../analyses/research-factory-2026-09-09/CATALOG.json). It is not another result
database. Each card preserves the catalog's stable `rq:` identifier, evidence cutoff, claim
identifiers, and exact report paths. The catalog remains authoritative for experiment records,
denominators, costs, and source hashes. Clearly labeled living updates currently include sealed
evidence through September11 on the updated individual cards; current summaries
are in [what we know](../analyses/CURRENT_SUMMARY.md) and the [live queue](../RESEARCH_QUEUE.md).
Individual frontmatter records each card's living cutoff. They do not change the catalog's earlier cutoff.

| Stable ID | Question | Catalog status | Publication readiness |
|---|---|---|---|
| `rq:correspondence` | [When do source cues survive full-system use?](correspondence.md) | promising exploratory | not ready |
| `rq:controller` | [Which root-training gains transfer?](controller-training.md) | promising but limited | not ready |
| `rq:reduction` | [Can roots reliably reduce supplied maps?](executed-reduction.md) | follow-up design priority | not ready |
| `rq:sufficient-interface` | [What information must cross a recursive boundary?](sufficient-interface.md) | instrument-limited pilot | not ready |
| `rq:continuation` | [Can compact state support fresh-root continuation?](continuation-state.md) | separate deferred line | not ready |
| `rq:adaptive-communication` | [Are resumable child handles worth their cost?](adaptive-communication.md) | deferred | not ready |
| `rq:counterfactual-credit` | [Can counterfactuals improve training-data selection?](counterfactual-credit.md) | deferred | not ready |
| `rq:latent-recursion` | [When should compute stay internal or become external decomposition?](latent-recursion.md) | deferred architecture | not ready |

## How to maintain this view

- Keep an existing `rq:` ID stable even if the wording or status changes. Add a new ID only for a
  genuinely different question.
- Treat evidence as append-only. Preserve contrary results, unavailable observations, and earlier
  interpretations; link later sealed updates in a distinct section rather than rewriting the
  catalog snapshot.
- Never turn a running, failed-before-model, or merely prepared job into evidence. Import a result
  only after its report and provenance boundary are sealed.
- Use [TEMPLATE.md](TEMPLATE.md) for a new card. A question becomes a paper candidate through
  supported claims, relevant baselines, explicit scope boundaries, and decisive replication—not
  through the number of runs.
- When a question matures, migrate its supported claims and counterevidence into paper claim cards.
  Keep the `rq:` ID as the lineage key and cite the authoritative catalog/report records rather than
  copying measurements into a new store.

The cards apply the brief reporting principles of claims, scope, reproducibility, limitations, and
compute from the [NeurIPS Paper Checklist](https://neurips.cc/public/guides/PaperChecklist). This
directory does not claim an independent detailed review of that checklist.
