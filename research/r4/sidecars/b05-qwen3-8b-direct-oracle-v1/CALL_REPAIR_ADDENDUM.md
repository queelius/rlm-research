# Additive collector-clock repair and oracle boundary

The sealed first entrypoint omitted `study.now`, which the inherited physical
`Collector.call` invokes before request construction, admission, HTTP dispatch, and final record
writing. The repaired namespace binds it to `time.time` and writes only to `attempt-002`.

The oracle arm is explicitly nondeployable: its prompt includes exact host-generated child reports.
It does not include the root answer. The direct arm includes neither reports nor the root answer.
This remains a model-alternative calibration, not a pure parameter-count or post-training effect.

