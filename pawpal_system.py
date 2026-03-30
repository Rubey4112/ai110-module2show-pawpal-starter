from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import Optional
from uuid import uuid4


class Priority(Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


@dataclass
class SchedulePlan:
    tasks: list[Task]
    reasoning: list[str]
    remaining_minutes: int


@dataclass
class Task:
    description: str
    duration_minutes: int
    priority: Priority
    frequency: str          # e.g. "daily", "weekly", "once"
    due_date: Optional[date] = None
    is_complete: bool = False
    id: str = field(default_factory=lambda: str(uuid4()))
    pet: Optional[Pet] = field(default=None, repr=False)

    def mark_complete(self) -> None:
        raise NotImplementedError

    def is_overdue(self) -> bool:
        raise NotImplementedError

    def is_due_today(self) -> bool:
        raise NotImplementedError


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)
    owner: Optional[Owner] = field(default=None, repr=False)

    def add_task(self, task: Task) -> None:
        raise NotImplementedError

    def remove_task(self, task_id: str) -> None:
        raise NotImplementedError

    def modify_task(self, task_id: str, updates: dict) -> None:
        raise NotImplementedError

    def list_tasks(self) -> list[Task]:
        raise NotImplementedError


class Owner:
    def __init__(self, name: str, email: str, available_minutes: int):
        self.name = name
        self.email = email
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        raise NotImplementedError

    def remove_pet(self, pet_name: str) -> None:
        raise NotImplementedError

    def list_pets(self) -> list[Pet]:
        raise NotImplementedError

    def get_all_tasks(self) -> list[Task]:
        raise NotImplementedError


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.total_minutes_available: int = owner.available_minutes
        self._cached_plan: Optional[SchedulePlan] = None

    def generate_plan(self) -> SchedulePlan:
        raise NotImplementedError

    def filter_by_priority(self, priority: Priority, tasks: Optional[list[Task]] = None) -> list[Task]:
        raise NotImplementedError

    def sort_by_priority(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        raise NotImplementedError

    def remaining_minutes(self, tasks: list[Task]) -> int:
        raise NotImplementedError
