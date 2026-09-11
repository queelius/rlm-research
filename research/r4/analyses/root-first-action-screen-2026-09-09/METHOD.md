# Posthoc first-action and cache-accounting screen

This is a descriptive follow-up to the completed original-versus-step8 root
comparison, not a new experiment or a preregistered mechanism test. Main inspected
all 48 first structured messages and one decoded raw response before writing this
method. That inspection found fewer usable first tool calls in the original arm
and an invalid JSON escape in one otherwise closed tool-call block.

Enumerate all 48 exported episodes, resolve each authenticated first root call,
decode its recorded output token IDs using the pinned local tokenizer, and apply
ordinary strict JSON decoding to a single closed tool-call block. Do not repair
the text, execute generated Python, or resample a model. Compare the syntax result
with the actual runtime's structured message, finish reason and token count.
Count lexical batching/JSON-decoding markers only in successfully decoded
`ipython` code; these are code-text observations, not proof that the program
executed a particular decomposition correctly. Missing or ambiguous cases remain
separate. The existing native first-action prefill is shared across arms, so
usable-call frequency is not a measure of freely choosing to call a tool.

Separately enumerate each distinct successful role-audit result referenced by
the 48 episodes. Reconcile raw wire usage with the saved native usage, retain
provider-reported cached prompt tokens when present, and report missingness.
Prompt tokens minus reported cached tokens are an accounting remainder, not a
measurement of physical compute or FLOPs. Service order was not counterbalanced.

Keep all original runs and the sealed root report unchanged. Save this supplement
in its own analysis directory, with source hashes, a script and focused checks.
