# Child-role suffix pilot

The authoritative full [design](../../ideas/2026-09-09-child-role-suffix-design.md), SHA `d1665da58c22172c921944b463af1847983d7f28a7afb5302749b5412d3ac708`, and [parent implementation decision](../../operations/2026-09-09-continuous-allocation/CHILD_ROLE_SUFFIX_IMPLEMENTATION_DECISION.md) define this study. This sidecar implements that one approved comparison; no training or GPU launch occurred during preparation.

Sixteen episodes: four previously exposed context/task groups × two fixed fresh seeds × unchanged versus depth-1 role suffix. Three groups were selected for costly failures; the fourth is the exposed moderate-cost 32-record comparator. Original root857a7ce6 and fixed childc32de129; no root prompt change, child request repair, grammar, forced recursion, retry addition, or tool removal.

The exact suffix is appended in the private runtime's nano `_start` before initial system/user messages are constructed, only at trusted depth1. A host-only ContextVar selects the overlay during the individual episode setup. HTTP mutation is used only for the established alias routing, never to insert the suffix. System instructions can conflict with a root request for code or an aggregate: retain the actual user request, mark possible conflicts for human review and do not interpret all nonuse as defiance.

Native graph/request/response capture and strict scoring are inherited. The numerical budget counts allowed final HTTP-request-hook entries immediately before transport, not proven server receipt or sampled completions. Prevented entries, request-only/canceled transport, recovered provider errors, empty answers and incomplete episodes remain distinct. A later global stop does not retroactively censor completed answers.

An owned1800-second envelope includes startup and cleanup; collection at most1500 seconds, four pair workers,2048 allowed native dispatch entries, no child-specific turn limit. Existing episode timeouts and >50% execution-error stop after8 attempts remain. Thus pathological controls may cause censoring; capped/partial low cost is not an efficiency win. The parent alone accepts and launches this job.

Primary units are attempted root episodes and four context clusters, with eight paired task/seed coordinates. Adaptive child trajectories are not paired by fiat. Strict answer preservation plus fewer physical calls/tokens would motivate a larger unselected replication, not a general-efficiency or end-to-end learning claim.
