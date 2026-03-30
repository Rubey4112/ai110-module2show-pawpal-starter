import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task, Priority, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# ── Owner bootstrap ────────────────────────────────────────────────────────────
if "owner" not in st.session_state:
    st.session_state.owner = None

if st.session_state.owner is None:
    st.subheader("Create Owner")
    with st.form("owner_form"):
        owner_name = st.text_input("Name", value="Jordan")
        owner_email = st.text_input("Email", value="jordan@example.com")
        available_minutes = st.number_input(
            "Available Minutes Today", min_value=10, max_value=480, value=120
        )
        if st.form_submit_button("Create Owner"):
            st.session_state.owner = Owner(
                name=owner_name,
                email=owner_email,
                available_minutes=int(available_minutes),
            )
            st.rerun()
    st.stop()

owner: Owner = st.session_state.owner
st.caption(f"Owner: **{owner.name}** · {owner.email} · {owner.available_minutes} min available today")

st.divider()

# ── Add pet ────────────────────────────────────────────────────────────────────
st.subheader("Add a Pet")
with st.form("add_pet_form"):
    col1, col2 = st.columns(2)
    with col1:
        pet_name = st.text_input("Name", value="Mochi")
        species = st.selectbox("Species", ["Dog", "Cat", "Rabbit", "Bird", "Other"])
    with col2:
        breed = st.text_input("Breed", value="Shiba Inu")
        age = st.number_input("Age (Years)", min_value=0, max_value=30, value=2)

    if st.form_submit_button("Add Pet"):
        existing_names = [p.name for p in owner.list_pets()]
        if pet_name.strip() == "":
            st.warning("Pet name cannot be empty.")
        elif pet_name in existing_names:
            st.warning(f"A pet named '{pet_name}' already exists.")
        else:
            owner.add_pet(Pet(name=pet_name, species=species, breed=breed, age=int(age)))
            st.success(f"Added {pet_name}!")
            st.rerun()

st.divider()

# ── Pets + tasks ───────────────────────────────────────────────────────────────
pets = owner.list_pets()

if not pets:
    st.info("No pets yet. Add one above.")
else:
    st.subheader("Pets & Tasks")
    for pet in pets:
        with st.expander(f"{pet.name} ({pet.species}, {pet.breed}, Age {pet.age})", expanded=True):
            tasks = pet.list_tasks()
            if tasks:
                rows = [
                    {
                        "Description": t.description,
                        "Duration (Min)": t.duration_minutes,
                        "Priority": t.priority.value.capitalize(),
                        "Frequency": t.frequency.capitalize(),
                        "Due": str(t.due_date) if t.due_date else "—",
                        "Done": "✓" if t.is_complete else "",
                    }
                    for t in tasks
                ]
                st.table(rows)
            else:
                st.caption("No tasks yet for this pet.")

            # Add-task form scoped to this pet
            st.markdown("**Add a Task**")
            # Checkbox must be outside the form so checking it triggers an immediate rerun
            use_due = st.checkbox("Set Due Date", key=f"usedue_{pet.name}")
            if use_due:
                st.date_input("Due Date", value=date.today(), key=f"due_{pet.name}")

            with st.form(f"add_task_{pet.name}"):
                c1, c2 = st.columns(2)
                with c1:
                    desc = st.text_input("Description", value="Morning Walk", key=f"desc_{pet.name}")
                    frequency = st.selectbox(
                        "Frequency", ["Daily", "Weekly", "Once"], key=f"freq_{pet.name}"
                    )
                with c2:
                    duration = st.number_input(
                        "Duration (Min)", min_value=1, max_value=240, value=20, key=f"dur_{pet.name}"
                    )
                    priority = st.selectbox(
                        "Priority",
                        [p.value.capitalize() for p in Priority],
                        index=0,
                        key=f"pri_{pet.name}",
                    )

                if st.form_submit_button("Add Task"):
                    if desc.strip() == "":
                        st.warning("Task description cannot be empty.")
                    else:
                        use_due = st.session_state.get(f"usedue_{pet.name}", False)
                        due_date = st.session_state.get(f"due_{pet.name}") if use_due else None
                        pet.add_task(
                            Task(
                                description=desc,
                                duration_minutes=int(duration),
                                priority=Priority(priority.lower()),
                                frequency=frequency.lower(),
                                due_date=due_date,
                            )
                        )
                        st.success(f"Task added to {pet.name}.")
                        st.rerun()

    st.divider()

    # ── Scheduler ──────────────────────────────────────────────────────────────
    st.subheader("Generate Schedule")
    if st.button("Generate Schedule"):
        scheduler = Scheduler(owner)
        plan = scheduler.generate_plan()

        if not plan.tasks:
            st.warning("No tasks could be scheduled (no incomplete tasks, or all tasks exceed available time).")
        else:
            st.success(f"Scheduled {len(plan.tasks)} task(s) · {plan.remaining_minutes} min remaining")
            rows = [
                {
                    "Pet": t.pet.name if t.pet else "—",
                    "Task": t.description,
                    "Duration (Min)": t.duration_minutes,
                    "Priority": t.priority.value.capitalize(),
                }
                for t in plan.tasks
            ]
            st.table(rows)

        st.markdown("**Scheduler Reasoning**")
        for line in plan.reasoning:
            st.markdown(f"- {line}")
