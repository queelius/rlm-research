# Why V1 does not answer direct versus Python

V1 produced zero Python final answers. Eight Python episodes ended on their first 512-token
inspection because generation hit the length cap mid-code and the unchanged fenced-cell parser
rejected it. The remaining two produced valid code: their first execution exposed a NumPy shape
mismatch, the second generation proposed a repair, and the third call timed out under the
45-second episode deadline. Direct returned a final answer for all ten cases.

Therefore V1 is an underbudgeted-interface diagnostic, not evidence that Python access is worse.
V2 keeps the same exposed ten cases, model, full-data Python access, direct view, total 2,048 output
tokens, parser, executor, scorer, temperature, and seed. It changes the episode deadline to 90
seconds for every arm and compares one 1,536-token inspection against three 512-token inspections;
both reserve at least 512 tokens for a final answer. A new direct arm in the same service is only a
service control. The comparison changes turn allocation and deadline relative to V1, and it is not
a pure computation-capability or generalization effect.

