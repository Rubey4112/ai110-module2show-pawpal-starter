from pawpal_system import Task, Pet, Priority


def test_mark_complete_changes_status():
    task = Task(
        description="Feed the cat",
        duration_minutes=5,
        priority=Priority.HIGH,
        frequency="daily",
    )
    assert task.is_complete is False
    task.mark_complete()
    assert task.is_complete is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Whiskers", species="cat", breed="Tabby", age=3)
    task = Task(
        description="Brush fur",
        duration_minutes=10,
        priority=Priority.LOW,
        frequency="weekly",
    )
    assert len(pet.tasks) == 0
    pet.add_task(task)
    assert len(pet.tasks) == 1
