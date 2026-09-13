"""Plain native collector with new physical cap and frozen plan, no live grading."""
import study
BASE=study.ROOT.parent/'b05-public-normalization-held9-v1'
with study.aliases({'study':study},BASE):previous=study.load('singleton_replica_plain_collector',BASE/'collect.py')
Collector=previous.Collector;execute=previous.execute;inherited=previous.inherited
