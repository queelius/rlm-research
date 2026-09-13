"""Reuse original plain native transport; all fixed calls regardless of model output."""
import study
BASE=study.ROOT.parent/'b05-public-normalization-held9-v1'
with study.aliases({'study':study},BASE):previous=study.load('singleton_plain_native_collector',BASE/'collect.py')
Collector=previous.Collector;execute=previous.execute;inherited=previous.inherited
