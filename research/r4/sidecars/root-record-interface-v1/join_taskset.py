"""Local taskset registration; the collector supplies every frozen JoinTask via RunSlot."""
from verifiers.v1.task import Task
from verifiers.v1.taskset import Taskset

__all__ = ['JoinTaskset']


class JoinTaskset(Taskset[Task]):
    def load(self):
        return ()
