# Additive terminal parser correction

After MAIN's terminal trigger, the sealed parser stopped at its first role/typed join. It incorrectly keyed both collections by filename rather than the internal authoritative `request_id`. Inspection found all 114 internal request IDs match in the first phase, while filenames are independently generated. No scoring output was published by that failed invocation.

`run_terminal_audit.py` authenticates the unchanged sealed parser and replaces only those two dictionary-key expressions. All scientific data, scoring rules, source seals and experiment outputs remain unchanged. This is an auditor bookkeeping correction, not a detected experiment defect. Subsequent execution authenticates the native request IDs against graph and wire evidence.
