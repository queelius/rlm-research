# Question-centered Markdown/YAML view of the research

User explicitly wants research questions linked to accumulated experimental evidence
so PhD reports, papers and research artifacts can be mined later. Work CPU only;
no GPU, model, lifecycle, queue or prior sealed catalog mutation. No subagents.

Own only new directory /project/alex_phd/runs/rlm-research-r4/questions and this
operation's question-cards-report.md. Use apply_patch for edits. Do not change
main repo, old user new-ideas, reports, JSON catalog or SQLite/DuckDB indexes.

Read existing analyses/research-factory-2026-09-09 README, CATALOG.json,
CLAIM_CARDS.md, DECISIONS.md and VALIDATION.json. Use exact stable rq IDs, claim
and experiment links. Add a lightweight navigation README and one Markdown page
per eight existing questions. YAML frontmatter: schema version, id, title, status,
updated_utc, evidence_cutoff, source_catalog path+SHA, related questions, claim IDs,
report paths and publication_readiness. Body in plain complete sentences: question,
why it matters, evidence so far including contrary findings, what remains unknown,
smallest discriminating next experiment, and what would justify a stronger claim.
Avoid run nicknames in headings; put exact names/hashes in metadata and links.

This is a generated/curated QUESTION VIEW, not a second conflicting result database.
Explicitly separate sealed catalog snapshot from later linked updates. Latest extra
sources: analyses/leaf-local-cue-replay-live-2026-09-09/REPORT.md (sealed) and
operations/2026-09-09-allocation-5780/audit-report.md (three-root bridge, sealed via
analyses/root-child-representation-bridge-panel-live-2026-09-09/FINAL_MANIFEST.json).
Bounded bridge allchecksum0; possible2countgain notrobustacrossroots; mapcontainer
misuse shows combining evidence bottleneck. Prepared current completeSFT is RUNNING,
NOT a result. Avoid copying mutable queue status into permanent result assertions.
For deferred ideas honestly say no experiment/no result, not implied positive support.

No framework, renderer, new database or installer. If a tiny validator helps, keep it
in this directory with focused tests; use installed PyYAML if present or avoid needing
new dependencies. Validate8 IDs/YAML, source hashes and every local link. Future
questions can use one minimal TEMPLATE.md; explain stableIDs, append-only evidence
and migration to paper claim cards. Source NeurIPS checklist https://neurips.cc/public/guides/PaperChecklist
only for brief reporting principles (claims/scope/reproducibility/limitations/compute);
MAIN browsed it but do not claim independent detailed review unless you read it.
Questions become papers through supported claims, baselines and boundaries, not
number of runs. Target a useful modest readable layer, not a research platform.
Report files/verification/limitations and content hashes; do not declare publication
ready. No automatic Git push or commits for external research artifacts.
