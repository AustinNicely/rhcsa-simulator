"""Task scheduling tasks - stub module."""
from tasks.base import SimpleTask
from tasks.registry import TaskRegistry

@TaskRegistry.register("scheduling")
class SchedulingStubTask(SimpleTask):
    def __init__(self):
        super().__init__("sched_001", "scheduling", "exam", 5,
                        "Scheduling tasks coming soon")
    def generate(self, **params):
        return self
