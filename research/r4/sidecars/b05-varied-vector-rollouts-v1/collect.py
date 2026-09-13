"""Unchanged four-worker plain-call graph, only the64-call study binding changes."""
import study
BASE=study.ROOT.parent/'b05-public-normalization-held9-v1'
with study.aliases({'study':study},BASE):previous=study.load('varied_vector_plain_collector',BASE/'collect.py')
Collector=previous.Collector;execute=previous.execute;inherited=previous.inherited
