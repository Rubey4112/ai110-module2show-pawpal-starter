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
    start_minute: Optional[int] = field(default=None, repr=False)

    @property
    def end_minute(self) -> Optional[int]:
        """Exclusive end time in minutes from the start of the day.

        Returns:
            int: ``start_minute + duration_minutes`` when ``start_minute`` is set.
            None: when the task has not yet been scheduled.
        """
        if self.start_minute is None:
            return None
        return self.start_minute + self.duration_minutes

    def mark_complete(self) -> Optional[Task]:
        """Mark this task as completed and schedule the next recurrence when applicable.

        For ``'daily'`` tasks the next occurrence is due tomorrow; for ``'weekly'``
        tasks it is due in seven days.  The new task is appended to the same pet
        automatically.

        Returns:
            Task: A new ``Task`` instance representing the next occurrence, with a
                fresh UUID and ``is_complete=False``, if the task is recurring and
                belongs to a pet.
            None: If the task is ``'once'`` or has no pet reference.
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
        """Check whether this task is past its due date and still incomplete.

        Returns:
            bool: ``True`` if ``due_date`` is set, is earlier than today, and
                ``is_complete`` is ``False``; ``False`` otherwise.
        """
        if self.due_date is None or self.is_complete:
            return False
        return self.due_date < date.today()

    def is_due_today(self) -> bool:
        """Check whether this task's due date is the current calendar date.

        Returns:
            bool: ``True`` if ``due_date`` equals today's date; ``False`` if
                ``due_date`` is ``None`` or on any other date.
        """
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
        """Append a task to this pet's task list and back-link it to this pet.

        Args:
            task (Task): The task to add.  Its ``pet`` attribute is set to
                ``self`` before appending.

        Returns:
            None
        """
        task.pet = self
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove a task from this pet's list by its unique ID.

        Args:
            task_id (str): The UUID string of the task to remove.  If no task
                with that ID exists the list is left unchanged.

        Returns:
            None
        """
        self.tasks = [t for t in self.tasks if t.id != task_id]

    def modify_task(self, task_id: str, updates: dict) -> None:
        """Update one or more fields of a task in-place.

        Args:
            task_id (str): The UUID string of the task to modify.
            updates (dict): A mapping of attribute names to new values.  Keys
                that do not correspond to real ``Task`` attributes are silently
                ignored.

        Returns:
            None
        """
        for task in self.tasks:
            if task.id == task_id:
                for key, value in updates.items():
                    if hasattr(task, key):
                        setattr(task, key, value)
                return

    def list_tasks(self) -> list[Task]:
        """Return all tasks belonging to this pet.

        Returns:
            list[Task]: A shallow copy of ``self.tasks``; mutating the returned
                list does not affect the pet's internal list.
        """
        return list(self.tasks)

    def filter_by_status(self, completed: bool) -> list[Task]:
        """Filter this pet's tasks by completion status.

        Args:
            completed (bool): Pass ``True`` to get completed tasks; ``False``
                to get incomplete tasks.

        Returns:
            list[Task]: Tasks whose ``is_complete`` flag equals ``completed``.
        """
        return [t for t in self.tasks if t.is_complete == completed]


class Owner:
    def __init__(self, name: str, email: str, available_minutes: int):
        """Initialise an Owner with basic profile info and an empty pet list.

        Args:
            name (str): The owner's full name.
            email (str): The owner's contact e-mail address.
            available_minutes (int): Total minutes the owner has available for
                pet-care tasks each day; used by ``Scheduler`` as the time budget.
        """
        self.name = name
        self.email = email
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's roster and back-link it to this owner.

        Args:
            pet (Pet): The pet to register.  Its ``owner`` attribute is set to
                ``self`` before appending.

        Returns:
            None
        """
        pet.owner = self
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from this owner's roster by name.

        Args:
            pet_name (str): The exact name of the pet to remove.  If no pet
                with that name exists the list is left unchanged.

        Returns:
            None
        """
        self.pets = [p for p in self.pets if p.name != pet_name]

    def list_pets(self) -> list[Pet]:
        """Return all pets registered to this owner.

        Returns:
            list[Pet]: A shallow copy of ``self.pets``; mutating the returned
                list does not affect the owner's internal roster.
        """
        return list(self.pets)

    def get_all_tasks(self) -> list[Task]:
        """Collect every task across all of this owner's pets into one flat list.

        Returns:
            list[Task]: Tasks from all pets in roster order, preserving each
                pet's internal task order.
        """
        return [task for pet in self.pets for task in pet.tasks]


class Scheduler:
    def __init__(self, owner: Owner):
        """Initialise the Scheduler for a specific owner.

        Args:
            owner (Owner): The owner whose pets' tasks will be scheduled.
                ``owner.available_minutes`` is captured as the total time budget.
        """
        self.owner = owner
        self.total_minutes_available: int = owner.available_minutes
        self._cached_plan: Optional[SchedulePlan] = None

    def _pet_label(self, task: Task) -> str:
        """Return a possessive label string for the pet that owns a task.

        Args:
            task (Task): The task whose ``pet`` attribute is inspected.

        Returns:
            str: ``"<PetName>'s "`` when the task is linked to a pet;
                an empty string ``""`` otherwise.
        """
        return f"{task.pet.name}'s " if task.pet else ""

    def generate_plan(self) -> SchedulePlan:
        """Build a priority-ordered daily schedule that fits within the owner's time budget.

        Incomplete tasks are sorted by priority (and urgency) then greedily
        assigned consecutive time slots.  Tasks that no longer fit are skipped
        with an explanatory note.  Any overlapping intervals are flagged as
        conflicts in the reasoning log.  The resulting plan is also cached on
        ``self._cached_plan`` for later inspection.

        Returns:
            SchedulePlan: A dataclass containing:
                - ``tasks`` – ordered list of scheduled ``Task`` objects with
                  ``start_minute`` set.
                - ``reasoning`` – human-readable strings explaining each
                  scheduling decision and any detected conflicts.
                - ``remaining_minutes`` – unused minutes after scheduling.
        """
        sorted_tasks = self.sort_by_priority(
            [t for t in self.owner.get_all_tasks() if not t.is_complete]
        )

        scheduled: list[Task] = []
        reasoning: list[str] = []
        minutes_used = 0

        for task in sorted_tasks:
            label = self._pet_label(task)
            remaining = self.total_minutes_available - minutes_used
            if task.duration_minutes <= remaining:
                task.start_minute = minutes_used
                scheduled.append(task)
                minutes_used += task.duration_minutes
                tag = " [OVERDUE]" if task.is_overdue() else " [due today]" if task.is_due_today() else ""
                reasoning.append(
                    f"Scheduled: {label}'{task.description}' ({task.priority.value} priority, "
                    f"{task.duration_minutes} min, starts at min {task.start_minute}){tag}"
                )
            else:
                reasoning.append(
                    f"Skipped: {label}'{task.description}' — not enough time remaining "
                    f"({task.duration_minutes} min needed, {remaining} min left)"
                )

        for a, b in self.detect_conflicts(scheduled):
            reasoning.append(
                f"CONFLICT: {self._pet_label(a)}'{a.description}' (min {a.start_minute}–{a.end_minute}) "
                f"overlaps {self._pet_label(b)}'{b.description}' (min {b.start_minute}–{b.end_minute})"
            )

        self._cached_plan = SchedulePlan(
            tasks=scheduled,
            reasoning=reasoning,
            remaining_minutes=self.total_minutes_available - minutes_used,
        )
        return self._cached_plan

    def detect_conflicts(self, tasks: Optional[list[Task]] = None) -> list[tuple[Task, Task]]:
        """Find all pairs of scheduled tasks whose time intervals overlap.

        Only tasks that have a ``start_minute`` assigned are examined.  The
        check works across different pets because the owner can only perform one
        activity at a time.

        Args:
            tasks (list[Task] | None): Explicit list of tasks to check.
                Defaults to all tasks across the owner's pets when ``None``.

        Returns:
            list[tuple[Task, Task]]: Each element is a pair ``(a, b)`` where
                task ``a``'s interval ``[start, start+duration)`` overlaps with
                task ``b``'s interval.  An empty list means no conflicts.
        """
        source = [t for t in (tasks or self.owner.get_all_tasks()) if t.start_minute is not None]
        conflicts: list[tuple[Task, Task]] = []
        for i, a in enumerate(source):
            for b in source[i + 1:]:
                assert a.start_minute is not None and b.start_minute is not None
                if a.start_minute < b.start_minute + b.duration_minutes and b.start_minute < a.start_minute + a.duration_minutes:
                    conflicts.append((a, b))
        return conflicts

    def filter_by_status(self, completed: bool, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Filter tasks by their completion status across all of the owner's pets.

        Args:
            completed (bool): ``True`` to return completed tasks; ``False`` for
                incomplete tasks.
            tasks (list[Task] | None): Explicit list to filter.  Falls back to
                all owner tasks when ``None``.

        Returns:
            list[Task]: Tasks whose ``is_complete`` flag equals ``completed``.
        """
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return [t for t in source if t.is_complete == completed]

    def filter_by_priority(self, priority: Priority, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Filter tasks to only those matching a specific priority level.

        Args:
            priority (Priority): The ``Priority`` enum value to filter by
                (``HIGH``, ``MEDIUM``, or ``LOW``).
            tasks (list[Task] | None): Explicit list to filter.  Falls back to
                all owner tasks when ``None``.

        Returns:
            list[Task]: Tasks whose ``priority`` attribute equals ``priority``.
        """
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return [t for t in source if t.priority == priority]

    def sort_by_priority(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Sort tasks from highest to lowest priority, promoting urgent tasks.

        The sort key is a three-tuple: ``(priority_rank, not_overdue, not_due_today)``.
        Within the same priority tier, overdue tasks come before tasks due today,
        which come before tasks with no urgency flag.

        Args:
            tasks (list[Task] | None): Explicit list to sort.  Falls back to
                all owner tasks when ``None``.

        Returns:
            list[Task]: A new sorted list; the original list is not mutated.
        """
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        return sorted(source, key=lambda t: (order[t.priority], not t.is_overdue(), not t.is_due_today()))

    def sort_by_time(self, tasks: Optional[list[Task]] = None) -> list[Task]:
        """Sort tasks by due date in ascending chronological order.

        Tasks without a ``due_date`` are placed at the end of the list.

        Args:
            tasks (list[Task] | None): Explicit list to sort.  Falls back to
                all owner tasks when ``None``.

        Returns:
            list[Task]: A new sorted list; the original list is not mutated.
        """
        source = tasks if tasks is not None else self.owner.get_all_tasks()
        return sorted(source, key=lambda t: (t.due_date is None, t.due_date or date.min))

    def remaining_minutes(self, tasks: list[Task]) -> int:
        """Calculate how many minutes remain after accounting for a set of tasks.

        Args:
            tasks (list[Task]): The tasks whose ``duration_minutes`` values are
                summed and subtracted from the owner's total available time.

        Returns:
            int: ``total_minutes_available`` minus the sum of all task durations.
                May be negative if the tasks exceed the available time.
        """
        used = sum(t.duration_minutes for t in tasks)
        return self.total_minutes_available - used
