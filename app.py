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

    # ── Filter & sort controls ──────────────────────────────────────────────
    fc1, fc2 = st.columns(2)
    with fc1:
        filter_status = st.selectbox(
            "Filter by Status", ["All", "Pending", "Completed"], key="filter_status"
        )
    with fc2:
        sort_by = st.selectbox(
            "Sort by", ["Default", "Priority", "Due Date"], key="sort_by"
        )

    _scheduler = Scheduler(owner)

    for pet in pets:
        with st.expander(f"{pet.name} ({pet.species}, {pet.breed}, Age {pet.age})", expanded=True):
            tasks = pet.list_tasks()

            # Apply filter
            if filter_status == "Pending":
                tasks = [t for t in tasks if not t.is_complete]
            elif filter_status == "Completed":
                tasks = [t for t in tasks if t.is_complete]

            # Apply sort
            if sort_by == "Priority":
                tasks = _scheduler.sort_by_priority(tasks)
            elif sort_by == "Due Date":
                tasks = _scheduler.sort_by_time(tasks)

            if tasks:
                # Header row
                h0, h1, h2, h3, h4, h5 = st.columns([4, 2, 2, 2, 2, 1])
                h0.markdown("**Description**")
                h1.markdown("**Duration**")
                h2.markdown("**Priority**")
                h3.markdown("**Frequency**")
                h4.markdown("**Due**")
                h5.markdown("**Done**")
                st.divider()

                for t in tasks:
                    c0, c1, c2, c3, c4, c5 = st.columns([4, 2, 2, 2, 2, 1])
                    label = t.description
                    if t.is_complete:
                        label = f"~~{label}~~"
                    c0.markdown(label)
                    c1.write(f"{t.duration_minutes} min")
                    _priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    _emoji = _priority_emoji.get(t.priority.value.lower(), "")
                    c2.markdown(f"{_emoji} {t.priority.value.capitalize()}")
                    c3.write(t.frequency.capitalize())
                    c4.write(str(t.due_date) if t.due_date else "—")
                    if t.is_complete:
                        c5.write("✓")
                    else:
                        if c5.button("✓", key=f"done_{t.id}", help="Mark complete"):
                            t.mark_complete()
                            st.rerun()
            else:
                st.caption("No tasks match the current filter.")

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
                    "Priority": {"high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}.get(t.priority.value.lower(), t.priority.value.capitalize()),
                }
                for t in plan.tasks
            ]
            st.table(rows)

        st.markdown("**Scheduler Reasoning**")
        for line in plan.reasoning:
            st.markdown(f"- {line}")
