"""Networking tasks - stub module."""
from tasks.base import SimpleTask
from tasks.registry import TaskRegistry

@TaskRegistry.register("networking")
class NetworkStubTask(SimpleTask):
    def __init__(self):
        super().__init__("net_001", "networking", "exam", 5,
                        "Network tasks coming soon")
    def generate(self, **params):
        return self
