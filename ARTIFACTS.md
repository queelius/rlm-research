# Artifact availability

## What is public now

The source code and slides are in the linked code repositories. This notebook
adds readable research records, selected experiment scripts, figure-data files,
and evidence manifests. Each exported file has a source hash in `MANIFEST.json`.

## Unpublished files

The main R4 research directory occupied approximately 154 GiB on the cluster at
the publication inventory. That includes much more than the materials a reader
needs to understand the research. It has **not** been uploaded as a Git repository.

Large run outputs, complete native request/response traces, frozen input tensors,
model weights, optimizer states, and checkpoints remain in the research store.
Some links in exported reports refer to these files. Such links point here until
a reviewed public artifact bundle is available; a tooltip retains the original
target. Plain paths in text or JSON are provenance, not public download URLs.

Evidence hashes prove which local artifacts a report refers to; they do not make
those artifacts accessible and do not constitute an independent reproduction.
The current publication is consequently a research notebook, not a complete
reproducibility release.

## The next artifact release

Select completed studies behind the central claims. Bundle their exact inputs,
configuration, compact results, raw evidence needed to check the claims, and
reconstruction instructions. Include unsuccessful comparisons and missing-outcome
records, not just positive examples. Review dataset redistribution rights and
remove credentials or private metadata before upload.

For each bundle, record a stable URL/revision, size, SHA-256, associated experiment
and claim IDs, license, and whether the bundle is sufficient to reanalyze results
or rerun the experiment. Publish heavy model artifacts separately; prefer an
adapter plus the exact base-model revision over a duplicate base-model download.

No external artifact host has been provisioned or billed by this publication.
