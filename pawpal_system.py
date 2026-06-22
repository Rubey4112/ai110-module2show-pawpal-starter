class Task:
    def __init__(self, name: str, duration: int, priority: int, is_recurring: bool):
        self.name = name
        self.duration = duration
        self.priority = priority
        self.is_recurring = is_recurring
        self._completed = False

    @property
    def is_completed(self) -> bool:
        return self._completed

    def mark_complete(self) -> None:
        self._completed = True

    def __repr__(self) -> str:
        status = "done" if self._completed else "pending"
        recurrence = "recurring" if self.is_recurring else "one-time"
        return (
            f"Task('{self.name}', priority={self.priority}, "
            f"duration={self.duration}min, {recurrence}, {status})"
        )


class Pet:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
        self.tasks: list[Task] = []

    @property
    def pending_tasks(self) -> list[Task]:
        return [task for task in self.tasks if not task.is_completed]

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def delete_task(self, task: Task) -> None:
        self.tasks.remove(task)

    def __repr__(self) -> str:
        return f"Pet('{self.name}', species='{self.species}', tasks={len(self.tasks)})"


class Owner:
    def __init__(self, name: str, available_time: int):
        self.name = name
        self.available_time = available_time
        self.pets: list[Pet] = []

    @property
    def all_tasks(self) -> list[Task]:
        return [task for pet in self.pets for task in pet.tasks]

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)

    def delete_pet(self, pet: Pet) -> None:
        self.pets.remove(pet)

    def __repr__(self) -> str:
        return (
            f"Owner('{self.name}', available='{self.available_time}', "
            f"pets={len(self.pets)})"
        )


class Scheduler:
    def generate_plan(self, owner: Owner) -> list[Task]:
        pending = sorted(
            [task for pet in owner.pets for task in pet.pending_tasks],
            key=lambda t: t.priority,
            reverse=True,
        )
        plan = []
        time_remaining = owner.available_time
        for task in pending:
            if task.duration <= time_remaining:
                plan.append(task)
                time_remaining -= task.duration
        return plan

    def filter_by_completion(self, owner: Owner, completed: bool) -> list[Task]:
        return [
            task
            for pet in owner.pets
            for task in pet.tasks
            if task.is_completed == completed
        ]

    def filter_by_pet_name(self, owner: Owner, pet_name: str) -> list[Task]:
        return [
            task
            for pet in owner.pets
            if pet.name == pet_name
            for task in pet.tasks
        ]

    def display_plan(self, owner: Owner) -> None:
        plan = self.generate_plan(owner)
        if not plan:
            print(f"No pending tasks for {owner.name}.")
            return
        total_time = sum(t.duration for t in plan)
        remaining = owner.available_time - total_time
        print(f"--- Care Plan for {owner.name} ---")
        for i, task in enumerate(plan, start=1):
            recurrence = "recurring" if task.is_recurring else "one-time"
            print(
                f"{i}. [{task.priority}] {task.name} "
                f"({task.duration} min, {recurrence})"
            )
        print(f"\nTotal: {total_time} min | Remaining: {remaining} min")
