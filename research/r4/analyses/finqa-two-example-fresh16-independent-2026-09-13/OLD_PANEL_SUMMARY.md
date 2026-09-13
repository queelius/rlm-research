# What the completed two-example result actually showed

On the original16 FinQA questions, direct answers scored1/16 and model-written arithmetic programs scored3/16. All calls were available. Two synthetic demonstrations made7/16 programs executable, up from0/16 without demonstrations, and removed all13 literal `#i` placeholder failures. This was learning from examples in the prompt, not a weight update.

Two program wins were straightforward and source-faithful: subtract the two requested debt values; calculate growth from the requested operating-profit years. The third obtained the correct lease-share ratio by summing rows that each contained both a total and its breakdown. That doubled both numerator and denominator, so the extra duplication canceled. The answer is correct, but the method is not reliable evidence selection.

The direct win correctly answered2000 for dollar-note issuance, while its program counterpart could not address the repeated table rows. Other executable programs still chose wrong years, columns or expense components. Noisy targets remain a separate limitation: for example, the direct S&P return is supported by the December2005 column while the official target uses January2005. Original scores were not repaired.

Conclusion: demonstrations improved use of the arithmetic interface, but evidence selection and composition remain weak. Three versus one on16 exposed questions is exploratory, not general superiority or a novel recursive method. The fresh16 replication keeps this condition fixed on different pages and seeds; cross-panel differences must not be called paired treatment effects.

Completed independent comparison SHA `a0983659d9d7622b9aed65a61ffee057a3b780bc33754a74d58016cc0376026f`; all16 mechanism review SHA `9646500405b42f1103f5cac63f69d2a271caa3c27065674b6b97e8f2e4e92a13`, under `analyses/finqa-two-example-independent-2026-09-12/outcome-001/`.
