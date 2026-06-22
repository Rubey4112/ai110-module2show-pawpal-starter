class Task:
    def __init__(self, name: str, duration: int, priority: int, is_recurring: bool):
        self.name = name
        self.duration = duration
        self.priority = priority
        self.is_recurring = is_recurring
        self._completed = False

    def mark_complete(self) -> None:
        self._completed = True


class Pet:
    def __init__(self, name: str, species: str):
        self.name = name
        self.species = species
        self.tasks: list[Task] = []


class Owner:
    def __init__(self, name: str, available_time: str):
        self.name = name
        self.available_time = available_time
        self.pets: list[Pet] = []


class Scheduler:
    def generate_plan(self, owner: Owner) -> list[Task]:
        pass
