from __future__ import annotations

from .pet import Pet
from .task import Task


class Owner:
    def __init__(self, name: str, email: str, available_minutes: int):
        self.name = name
        self.email = email
        self.available_minutes = available_minutes
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def remove_pet(self, pet_name: str) -> None:
        pass

    def list_pets(self) -> list[Pet]:
        pass

    def get_all_tasks(self) -> list[Task]:
        pass
