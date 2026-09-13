"""Unmodified plain native collector and four-stage-worker graph."""
import study
BASE=study.PRIOR.parent/'b05-public-normalization-held9-v1'
with study.aliases({'study':study},BASE):previous=study.load('vector_plain_native_collector',BASE/'collect.py')
Collector=previous.Collector;execute=previous.execute;inherited=previous.inherited
