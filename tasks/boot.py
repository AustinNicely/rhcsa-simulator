"""Boot target tasks - stub module."""
from tasks.base import SimpleTask
from tasks.registry import TaskRegistry

@TaskRegistry.register("boot")
class BootStubTask(SimpleTask):
    def __init__(self):
        super().__init__("boot_001", "boot", "exam", 5,
                        "Boot tasks coming soon")
    def generate(self, **params):
        return self
