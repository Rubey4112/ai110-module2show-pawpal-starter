import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(name="Feed", duration=5, priority=1, is_recurring=True)
    assert not task.is_completed
    task.mark_complete()
    assert task.is_completed


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Buddy", species="dog")
    assert len(pet.tasks) == 0
    task = Task(name="Walk", duration=30, priority=2, is_recurring=False)
    pet.add_task(task)
    assert len(pet.tasks) == 1
