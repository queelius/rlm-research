# RLM research: navigation

The new 48-hour A100 allocation is active. Start with the
[live queue](RESEARCH_QUEUE.md) for actual running jobs, accepted successors,
completed work and recorded scheduling costs. The
[allocation plan](operations/2026-09-09-allocation-5780/PLAN.md) is the session ledger;
the earlier transfer handoff is historical.

Start with [what we know so far](analyses/CURRENT_SUMMARY.md) for the latest
plain-language findings and their limits. Then use the
[research dossier](analyses/cross-experiment-synthesis-2026-09-09/README.md) for
the wider research history, sources and proposed comparisons. Neither requires
reading raw logs first.

For completed work after the dossier's evidence cutoff, use the
[analysis reading guide](analyses/README.md). For current execution, use the
[live queue](RESEARCH_QUEUE.md).

The [linked research catalog](analyses/research-factory-2026-09-09/README.md)
connects recent questions, experiments, claims, decisions and publication gaps.
It is a bounded first slice with an explicit cutoff, not a replacement for all
historical reports or their immutable evidence.

The [research-question pages](questions/README.md) provide the Markdown + YAML
view: one stable question, its supporting and contrary evidence, what remains
unknown, and the smallest useful next test. Running work is not a result, and
proposed publication claims stay separate from established findings.

## Two different kinds of document

- The [live research queue](RESEARCH_QUEUE.md) states what is running, ready, or
  being prepared. It is the current execution handoff, not a results paper.
- The [dossier](analyses/cross-experiment-synthesis-2026-09-09/README.md) synthesizes
  completed evidence. Read its overview first, findings second, and experiment
  catalog or source inventory when checking a particular claim.

## Where the material lives

| Location | Purpose |
|---|---|
| `analyses/` | Human-readable reports and machine-readable evidence audits. |
| `questions/` | Linked question cards with YAML metadata, evidence and decision criteria. |
| `ideas/` | Research questions, literature connections, and proposed follow-ups. |
| `sidecars/` | Isolated experiment code, frozen specifications, and their outputs. |
| `operations/` | Launch ownership, scheduling, session handoffs, and decision records. |
| `operations/queue-history/` | Exact snapshots of earlier queues, separated from current status. |
| `shared/`, `catalog/` | Reusable inputs and provenance indexes. |
| `attempts/`, `campaigns/`, `exploratory/`, `validation/`, `legacy/` | Earlier experiment organizations; original paths are preserved. |

Large external models, datasets, and environments remain outside this research
store in the project research cache and environment stores. Source repositories
remain under `/project/alex_phd/repos/`. No raw experiment artifacts were moved to
create this navigation layer.

Names and short finding identifiers are for traceability. Conclusions should be
expressed in plain language, with observed results distinguished from explanations
and proposed next steps. Incomplete or invalid experiments are not successful
results, and repeated measurements are not new independent test examples.
