from datetime import date
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

# --- Setup ---
owner = Owner(name="Alex Rivera", email="alex@example.com", available_minutes=120)

# --- Pets ---
buddy = Pet(name="Buddy", species="Dog", breed="Labrador", age=3)
whiskers = Pet(name="Whiskers", species="Cat", breed="Siamese", age=5)

owner.add_pet(buddy)
owner.add_pet(whiskers)

# --- Tasks for Buddy ---
buddy.add_task(Task(
    description="Morning walk",
    duration_minutes=30,
    priority=Priority.HIGH,
    frequency="daily",
    due_date=date.today(),
))
buddy.add_task(Task(
    description="Brush fur",
    duration_minutes=15,
    priority=Priority.MEDIUM,
    frequency="weekly",
    due_date=date.today(),
))

# --- Tasks for Whiskers ---
whiskers.add_task(Task(
    description="Clean litter box",
    duration_minutes=10,
    priority=Priority.HIGH,
    frequency="daily",
    due_date=date.today(),
))
whiskers.add_task(Task(
    description="Playtime with feather toy",
    duration_minutes=20,
    priority=Priority.LOW,
    frequency="daily",
))
whiskers.add_task(Task(
    description="Administer flea medication",
    duration_minutes=5,
    priority=Priority.HIGH,
    frequency="monthly",
    due_date=date.today(),
))

# --- Generate Schedule ---
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

# --- Print Today's Schedule ---
print("=" * 45)
print("          TODAY'S SCHEDULE")
print(f"          Owner: {owner.name}")
print("=" * 45)

for i, task in enumerate(plan.tasks, start=1):
    pet_name = task.pet.name if task.pet else "Unknown"
    print(f"{i}. [{pet_name}] {task.description}")
    print(f"   Priority: {task.priority.value} | Duration: {task.duration_minutes} min")

print("-" * 45)
print(f"Total time used : {owner.available_minutes - plan.remaining_minutes} min")
print(f"Time remaining  : {plan.remaining_minutes} min")
print("=" * 45)
print("\nScheduling Notes:")
for note in plan.reasoning:
    print(f"  - {note}")
