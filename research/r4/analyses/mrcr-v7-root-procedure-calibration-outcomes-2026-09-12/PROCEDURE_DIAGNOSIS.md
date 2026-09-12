# V7 procedure diagnosis

The main failure is representation-aware retrieval, not a lack of model calls. In 31/32 episodes
the model opened `/context.txt`; 23 programs split it into individual lines and two used blank-line
splits. No program explicitly paired `User:` records with their following `Assistant:` response.
Fifteen post-marker answers are verbatim context substrings, but 12 answers contain a `User:` request
line and three contain an `Assistant:` label or fragment. Other answers fabricate/formalize content,
truncate an arbitrary segment, or report that the desired record is absent. None is exact gold.

The apparent `\\n` issue is not a wrapper defect in these records. Tool arguments are JSON strings,
so raw audit JSON displays escaped newlines; `json.loads(arguments)["code"]` contains real Python
newlines. One episode did generate an unterminated f-string with a real newline before the closing
quote, producing the observed `SyntaxError`; its next model turn repaired the quote. Two other
episodes have model-code exceptions. These are genuine code errors, not transport escaping.

The short32 campaign changes the source representation to the exact original JSON, so its outcome
will test whether explicit structure is enough. If it still has zero exact retrieval, the most direct
architecture comparison is a prospectively frozen neutral schema/record-boundary preview versus
unchanged raw JSON on the same exact-verifier tasks. Such a preview can explain User/Assistant
pairing and boundaries, but must not reveal a target position, keyword, or gold answer.
