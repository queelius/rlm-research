---
date: 2026-09-10
status: additive_post_terminal_amendment
---

# Prospective reader amendment

The frozen prospective `audit.py` was amended after terminal release because its exact-list-order
assertion confused concurrent collector completion order with plan identity. The amendment replaces
that assertion with exact unique-ID membership plus full coordinate equality. It changes neither
scores nor planned membership. `native_recount.py` and `checkpoint_recount.py` are explicitly
post-terminal additions requested by MAIN; they are not represented as prospective methods. The
native recount independently re-decodes raw tokens but deliberately reuses the pinned trusted
producer protocol/scorer, so it is a consistency/replay audit rather than an independent metric
implementation.
