from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Task:
    description: str
    duration_minutes: int
    priority: str           # e.g. "high", "medium", "low"
    frequency: str          # e.g. "daily", "weekly", "once"
    due_date: Optional[date] = None
    is_complete: bool = False

    def mark_complete(self) -> None:
        pass

    def is_overdue(self) -> bool:
        pass

    def is_due_today(self) -> bool:
        pass
