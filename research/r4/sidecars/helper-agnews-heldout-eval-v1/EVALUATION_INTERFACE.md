# Frozen AG heldout256 evaluation

Three independent owners evaluate identical 64 batch-four, temperature-zero calls: original c32,
authenticated reference T1 checkpoint-0004, and the new AG checkpoint-0004. The new arm is
conditional on an exact four-update terminal plus authenticated step/state/commit/binding closure.
Each output remains separate under `outputs/{arm}-001`; unavailable and invalid calls are retained.
Gold is loaded only by host-side summarization and never enters a request body.
