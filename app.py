import streamlit as st

# Step 1: bring the logic-layer classes into the Streamlit app.
from pawpal_system import Owner, Pet, Scheduler, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown("Plan your pets' daily care tasks. Add pets, give them tasks, then build a schedule.")

# Step 2: persist the Owner across reruns using st.session_state.
# Streamlit reruns this script top-to-bottom on every interaction, so we only
# create the Owner once and reuse the stored instance on later reruns.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="Jordan")

owner: Owner = st.session_state.owner

st.divider()

# --- Owner ----------------------------------------------------------------
st.subheader("Owner")
owner.name = st.text_input("Owner name", value=owner.name)

st.divider()

# --- Add a pet ------------------------------------------------------------
st.subheader("Add a Pet")
with st.form("add_pet_form", clear_on_submit=True):
    pet_name = st.text_input("Pet name", value="")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    breed = st.text_input("Breed (optional)", value="")
    submitted_pet = st.form_submit_button("Add pet")
    if submitted_pet:
        if pet_name.strip():
            # Step 3: the form data is handled by Owner.add_pet().
            owner.add_pet(Pet(name=pet_name.strip(), species=species, breed=breed.strip()))
            st.success(f"Added {pet_name.strip()}.")
        else:
            st.error("Please enter a pet name.")

if not owner.pets:
    st.info("No pets yet. Add one above to get started.")

st.divider()

# --- Add a task to a pet --------------------------------------------------
if owner.pets:
    st.subheader("Add a Task")
    pet_names = [pet.name for pet in owner.pets]
    with st.form("add_task_form", clear_on_submit=True):
        target_pet_name = st.selectbox("For which pet?", pet_names)
        task_title = st.text_input("Task title", value="Morning walk")
        task_time = st.text_input("Time (HH:MM)", value="08:00")
        col1, col2 = st.columns(2)
        with col1:
            duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
        with col2:
            priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
        submitted_task = st.form_submit_button("Add task")
        if submitted_task:
            target_pet = next(p for p in owner.pets if p.name == target_pet_name)
            # The task is handled by Pet.add_task().
            target_pet.add_task(
                Task(
                    description=task_title,
                    time=task_time,
                    duration=int(duration),
                    priority=priority,
                )
            )
            st.success(f"Added '{task_title}' for {target_pet_name}.")

    # Show current pets and their tasks.
    st.markdown("### Current Pets & Tasks")
    for pet in owner.pets:
        st.markdown(f"**{pet.describe()}** — {pet.task_count()} task(s)")
        if pet.tasks:
            st.table(
                [
                    {
                        "time": t.time,
                        "task": t.description,
                        "duration": t.duration,
                        "priority": t.priority,
                        "done": t.completed,
                    }
                    for t in pet.tasks
                ]
            )

st.divider()

# --- Build schedule -------------------------------------------------------
st.subheader("Build Schedule")
if st.button("Generate schedule"):
    if owner.get_all_tasks():
        scheduler = Scheduler(owner)

        # Surface conflicts first so the owner sees clashes before the plan.
        conflicts = scheduler.detect_conflicts()
        if conflicts:
            for warning in conflicts:
                st.warning(warning)
        else:
            st.success("No scheduling conflicts found. 🎉")

        # Show the time-sorted plan as a clean, professional table.
        st.markdown(f"#### Today's Schedule for {owner.name}")
        st.table(
            [
                {
                    "time": task.time or "—",
                    "task": task.description,
                    "pet": pet.name,
                    "duration": task.duration,
                    "priority": task.priority,
                    "done": task.completed,
                }
                for pet, task in scheduler.sort_by_time()
            ]
        )
    else:
        st.warning("Add at least one task before generating a schedule.")
