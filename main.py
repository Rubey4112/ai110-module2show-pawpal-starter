from pawpal_system import Owner, Pet, Task, Scheduler

owner = Owner("Alex", 480)

dog = Pet("Buddy", "Dog")
cat = Pet("Whiskers", "Cat")

dog.add_task(Task("Morning walk",      duration=30, priority=3, is_recurring=True))
dog.add_task(Task("Flea medication",   duration=5,  priority=2, is_recurring=False))
cat.add_task(Task("Clean litter box",  duration=10, priority=3, is_recurring=True))
cat.add_task(Task("Vet checkup",       duration=60, priority=1, is_recurring=False))
cat.add_task(Task("Evening play time", duration=15, priority=2, is_recurring=True))

owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler()

print("===== Today's Schedule =====")
scheduler.display_plan(owner)
