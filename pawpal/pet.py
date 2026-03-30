from __future__ import annotations
from dataclasses import dataclass, field

from .task import Task


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_description: str) -> None:
        pass

    def modify_task(self, task_description: str, updates: dict) -> None:
        pass

    def list_tasks(self) -> list[Task]:
        pass
