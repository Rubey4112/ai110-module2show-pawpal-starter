from __future__ import annotations
from dataclasses import dataclass, field, replace
from datetime import date, timedelta
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

    def mark_complete(self) -> Optional[Task]:
        """Mark this task as completed.

        For 'daily' and 'weekly' tasks, automatically adds the next occurrence
        to the pet with a new due date (today + 1 day or today + 7 days).
        Returns the newly created task, or None if no recurrence applies.
        """
        self.is_complete = True
        recurrence_days = {"daily": 1, "weekly": 7}
        if self.frequency in recurrence_days and self.pet is not None:
            next_task = replace(
                self,
                due_date=date.today() + timedelta(days=recurrence_days[self.frequency]),
                is_complete=False,
                id=str(uuid4()),
            )
            self.pet.add_task(next_task)
            return next_task
        return None

    def is_overdue(self) -> bool:
        """Return True if the task has a past due date and is not complete."""
        if self.due_date is None or self.is_complete:
            return False
        return self.due_date < date.today()

    def is_due_today(self) -> bool:
        """Return True if the task's due date is today."""
        if self.due_date is None:
            return False
        return self.due_date == date.today()


@dataclass
class Pet:
    name: str
    species: str
    breed: str
    age: int
    tasks: list[Task] = field(default_factory=list)
    owner: Optional[Owner] = field(default=None, repr=False)

    def add_task(self, task: Task) -> None:
        """Append a task to this pet's task list and set its pet reference."""
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given ID from this pet's task list."""
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def modify_task(self, task_id: str, updates: dict) -> None:
        """Update fields of the task matching task_id with values from updates."""
        for task in self.tasks:
            if task.id == task_id:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                return

    def list_tasks(self) -> list[Task]:
        """Return a shallow copy of this pet's task list."""
        return list(self.tasks)

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Return tasks matching the given completion status."""
        return [t for t in self.tasks if t.is_complete == completed]


class Owner:
    def __init__(self, name: str, email: str, available_minutes: int):
        self.name = name
        self.email = email
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list and set its owner reference."""
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove the pet with the given name from this owner's list."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def list_pets(self) -> list[Pet]:
        """Return a shallow copy of this owner's pet list."""
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Return a flat list of all tasks across every pet."""
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.total_minutes_available: int = owner.available_minutes
        self._cached_plan: Optional[SchedulePlan] = None

    def generate_plan(self) -> SchedulePlan:
        """Build and return a priority-ordered schedule that fits within available time."""
        all_tasks = self.owner.get_all_tasks()
        incomplete = [t for t in all_tasks if not t.is_complete]
        sorted_tasks = self.sort_by_priority(incomplete)

        scheduled: list[Task] = []
        reasoning: list[str] = []
        minutes_used = 0

        for task in sorted_tasks:
            pet_label = f"{task.pet.name}'s " if task.pet else ""
            if minutes_used + task.duration_minutes <= self.total_minutes_available:
                scheduled.append(task)
                minutes_used += task.duration_minutes
                note = f"Scheduled: {pet_label}'{task.description}' ({task.priority.value} priority, {task.duration_minutes} min)"
                if task.is_overdue():
                    note += " [OVERDUE]"
                elif task.is_due_today():
                    note += " [due today]"
                reasoning.append(note)
            else:
                reasoning.append(
                    f"Skipped: {pet_label}'{task.description}' — not enough time remaining "
                    f"({task.duration_minutes} min needed, {self.total_minutes_available - minutes_used} min left)"
                )

        self._cached_plan = SchedulePlan(
            tasks=scheduled,
            reasoning=reasoning,
            remaining_minutes=self.total_minutes_available - minutes_used,
        )
        return self._cached_plan

    def filter_by_status(self, completed: bool, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return tasks matching the given completion status across all pets."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return [t for t in source if t.is_complete == completed]

    def filter_by_priority(self, priority: Priority, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Return only the tasks that match the given priority level."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return [t for t in source if t.priority == priority]

    def sort_by_priority(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Sort tasks high-to-low by priority, with overdue and due-today tasks first."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(source, key=lambda t: (order[t.priority], not t.is_overdue(), not t.is_due_today()))

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Sort tasks by due_date ascending. Tasks without a due date sort to the end."""
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(source, key=lambda t: (t.due_date is None, t.due_date or date.min))

    def remaining_minutes(self, tasks: list[Task]) -> int:
        """Return available minutes minus the total duration of the given tasks."""
        used = sum(t.duration_minutes for t in tasks)
        return self.total_minutes_available - used
