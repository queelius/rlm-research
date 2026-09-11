# Additive factual caveat after CPU_READY

2026-09-09. Original READY ab16721ee537df09370d534d63fa4d8d542df1e1a17c903efac7c711c1a837d0
and all sources remain unchanged. This note is outside that original frozen closure;
MAIN may bind it separately in acceptance.

`bridge_config.json`, installed in each new runtime, contains the assigned representation
and public ID/text catalog. It is unadvertised in the root prompt but root-readable and
root-writable, like the surrounding runtime filesystem. Therefore this is NOT a sealed
treatment-blind interface. A root could inspect the configuration or installed overlay.
Within each task pair the initial native root prompt, tools, public API, records and
worked example are identical, but the entire runtime filesystem is not byte-identical.
DESIGN's statement about equal public files refers to the public records/API surface,
not this study configuration. Subsequent policy changes could reflect inspection as
well as different child evidence; report actual root actions if inspection occurs.

Configuration is loaded into the supervisor before root model execution. Editing a file
later does not establish a changed in-memory trusted invocation decision. Host-native
grammar eligibility independently matches the host catalog and trusted role/depth.
This is still not cryptographic isolation from arbitrary runtime code. Event files are
root-writable claims and require native prompt/token/invocation/graph corroboration.
No source, prompt, sampling, output or behavioral change accompanies this clarification.
