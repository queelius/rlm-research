# Implementation report

This isolated sidecar reuses the accepted child-interface trainer, native scorer/collector, and
current registered service lifecycle. The prepared mixed stream is byte-for-byte composed from the
predecessor's frozen rows at the same indices: full6 for six contexts, then ABO for six, repeated.
It contains 96 contexts, 1,536 unique source groups, 23,214 supervised target tokens, and exactly
eight contexts per interface for each of six train pairs.

The 192 readout coordinates preserve the old panels, contexts, pairs, record order, and stochastic
seeds. Only the new policy alias, dispatch order, and derived call ID differ. Old c32/full6/ABO
controls are frozen receipts and are not called again. CPU tests exercise exact row identity,
coordinate reuse, balanced schedule, masking, fixed-last selection, NULL-aware metrics, native raw
transport, unknown finish-reason rejection, owner launcher registration, and failure accounting.
