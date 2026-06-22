import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}

# ── Session state init ──────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None
if "pets" not in st.session_state:
    st.session_state.pets = []

# ── Owner setup ─────────────────────────────────────────────────────────────
st.subheader("Owner")
col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
with col2:
    available_time = st.number_input("Available time (min)", min_value=1, max_value=1440, value=60)

if st.button("Set owner"):
    st.session_state.owner = Owner(owner_name, available_time)
    st.session_state.pets = []
    st.success(f"Owner set: {owner_name} ({available_time} min available)")

owner = st.session_state.owner

st.divider()

# ── Pet management ──────────────────────────────────────────────────────────
st.subheader("Pets")

if owner is None:
    st.info("Set an owner above before adding pets.")
else:
    pcol1, pcol2, pcol3 = st.columns(3)
    with pcol1:
        pet_name = st.text_input("Pet name", value="Mochi")
    with pcol2:
        species = st.selectbox("Species", ["dog", "cat", "other"])
    with pcol3:
        st.write("")
        st.write("")
        if st.button("Add pet"):
            pet = Pet(pet_name, species)
            owner.add_pet(pet)
            st.session_state.pets = owner.pets
            st.success(f"Added {pet_name} the {species}.")

    if owner.pets:
        st.write("Current pets:", [p.name for p in owner.pets])

st.divider()

# ── Task management ─────────────────────────────────────────────────────────
st.subheader("Tasks")

if owner is None or not owner.pets:
    st.info("Add an owner and at least one pet before adding tasks.")
else:
    pet_names = [p.name for p in owner.pets]
    tcol1, tcol2 = st.columns(2)
    with tcol1:
        selected_pet_name = st.selectbox("Pet", pet_names)
        task_name = st.text_input("Task name", value="Morning walk")
    with tcol2:
        duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        is_recurring = st.checkbox("Recurring")

    if st.button("Add task"):
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        task = Task(task_name, duration, PRIORITY_MAP[priority], is_recurring)
        target_pet.add_task(task)
        st.success(f"Added '{task_name}' to {selected_pet_name}.")

    for pet in owner.pets:
        if pet.tasks:
            st.markdown(f"**{pet.name}'s tasks**")
            rows = [
                {
                    "Task": t.name,
                    "Duration (min)": t.duration,
                    "Priority": t.priority,
                    "Recurring": t.is_recurring,
                    "Done": t.is_completed,
                }
                for t in pet.tasks
            ]
            st.table(rows)

st.divider()

# ── Schedule generation ──────────────────────────────────────────────────────
st.subheader("Generate Schedule")

if owner is None or not owner.pets or not owner.all_tasks:
    st.info("Add an owner, pet(s), and at least one task to generate a schedule.")
else:
    if st.button("Generate schedule"):
        scheduler = Scheduler()
        plan = scheduler.generate_plan(owner)

        if not plan:
            st.warning("No tasks fit within the available time.")
        else:
            total_time = sum(t.duration for t in plan)
            remaining = owner.available_time - total_time

            st.success(f"Care plan for **{owner.name}** — {total_time} min used, {remaining} min remaining")
            for i, task in enumerate(plan, start=1):
                recurrence = "recurring" if task.is_recurring else "one-time"
                st.markdown(
                    f"**{i}.** [{task.priority}] {task.name} — {task.duration} min, {recurrence}"
                )

        skipped = [t for t in owner.all_tasks if not t.is_completed and t not in plan]
        if skipped:
            st.caption(f"Skipped (no time): {', '.join(t.name for t in skipped)}")
