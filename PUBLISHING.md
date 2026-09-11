# Publishing policy

## Scope and organization

Keep runtime development in its existing repositories. Publish a curated reading
view here, preserving the source hierarchy under `research/<round>/` so related
questions, claims, analyses, and experiment designs remain connected.

The first snapshot includes Markdown research records, top-level R4 experiment
scripts, selected small figure-data and evidence-manifest JSON files, and source
repository identities. Historical campaign, study, run, and status records are
retained separately. The source
store remains authoritative for raw run outputs.

## Size budget

- Publication limit: **5 MiB per file** and **50 MiB total exported content** for
  this initial snapshot. These are our stricter local budgets, not GitHub limits.
- Keep Git history small; review history size before each refresh. Repeated small
  snapshots still accumulate history. Revisit storage before history reaches 250 MiB.
- GitHub blocks ordinary Git files larger than 100 MiB and warns above 50 MiB.
  It recommends repositories ideally below 1 GB, and strongly recommends below 5 GB.
  Those repository figures are recommendations, not a promise of unlimited capacity.
  [GitHub's current limits](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github).

Git LFS is available but is not the default for the research working directory.
It has separate limits and storage/bandwidth accounting; do not enable a bulk LFS
upload without checking the account's allowance and expected download costs.

## Keep out of Git

Do not upload environments, caches, downloaded base models, optimizer states,
large raw traces, credentials, session transcripts, or unrelated projects.
Do not copy third-party datasets or repositories wholesale. Retain source URLs,
revisions, hashes, and licenses instead.

Useful large artifacts can be published separately, for example through a
[Hugging Face dataset or model repository](https://huggingface.co/docs/hub/en/repositories),
or as a versioned research release linked from this notebook. A paper-ready
snapshot can also use [Zenodo's GitHub integration](https://help.zenodo.org/docs/github/)
for archival publication. No such artifact upload is implied by this first snapshot.

## Refresh procedure

1. Read from the research store without modifying active jobs or moving their files.
2. Select the same explicit document/code categories. Review new categories rather
   than running `git add` against `/project/alex_phd` or a complete run tree.
3. Record every original file's SHA-256, relative publication path, size, and read
   time in the manifest. Preserve source text apart from documented link rewriting.
4. Exclude and report files that exceed the size budget or match credential checks.
   Scan for private data as well; an automated token-pattern scan is not a guarantee.
5. Rewrite links to included files. Mark omitted artifacts explicitly. Keep
   corrections adjacent to the reports they qualify.
6. Verify file hashes, link targets, size totals, and the staged Git diff before
   committing and pushing. Publish a named cutoff; do not describe old queue notes
   as live status.

The current snapshot is a deliberately small publication layer. It does not
relocate the experiment store or add a new prerequisite to GPU research.
