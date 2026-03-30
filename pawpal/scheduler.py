from __future__ import annotations

from .owner import Owner
from .task import Task


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.total_minutes_available: int = owner.available_minutes

    def generate_plan(self) -> list[Task]:
        pass

    def get_reasoning(self) -> list[str]:
        pass

    def filter_by_priority(self, priority: str) -> list[Task]:
        pass

    def sort_by_priority(self) -> list[Task]:
        pass
