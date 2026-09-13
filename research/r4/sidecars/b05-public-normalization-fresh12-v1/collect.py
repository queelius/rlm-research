"""Unchanged plain collector/graph with new frozen task bindings."""
import study
with study.aliases({'study':study},study.PRIOR):
    previous=study.load('fresh_normalization_collector',study.PRIOR/'collect.py')
Collector=previous.Collector;execute=previous.execute;inherited=previous.inherited
