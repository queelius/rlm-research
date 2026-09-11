# Prospective parser amendment 1

At `2026-09-10T00:20:40Z`, still before any science output existed, a dry run against the empty
attempt directory found that missing-row records omitted the derived `zero_gold` field and caused
summary construction to raise `KeyError`. The amendment adds only that host-gold-derived field to
the missing-row branch. It changes no inputs, scoring, availability rule, native authentication,
dataflow rule, or planned denominator. Original parser SHA-256:
`6a963be43871f3a0a12942e17d1ab4f5ab1be88358d92b7d5dc9a294c9c096b1`.
