"""Container (Podman) tasks - stub module."""
from tasks.base import SimpleTask
from tasks.registry import TaskRegistry

@TaskRegistry.register("containers")
class ContainerStubTask(SimpleTask):
    def __init__(self):
        super().__init__("container_001", "containers", "exam", 5,
                        "Container tasks coming soon")
    def generate(self, **params):
        return self
