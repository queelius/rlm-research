# Preserved engineering failures

pilot-001: exited before GPU/service startup. JSONL file was valid; Python
str.splitlines() split literal Unicode line separators inside LongBench document
strings. Version2 reads physical lines from the file stream. The original data,
owner source and first admission remain unchanged. No scientific calls occurred.

pilot-002: model startup succeeded but installed Transformers returned
BatchEncoding from apply_chat_template; native JSON serialization failed before
dispatch. The32 episodes contain explicit admission errors, zero model calls.
GPU science interval12.45seconds produced no useful work, then owner released.
Version3 uses runner_v2, explicitly return_dict=False; an actual installed-
tokenizer regression test checks the native prefix representation. An admission-
error-only batch now stops the service too, not just HTTP errors.
