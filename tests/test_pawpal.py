"""Automated tests for core PawPal+ behaviors.

Covers happy paths (sorting, recurrence, conflict detection) and edge cases
(a pet with no tasks, two tasks at the exact same time).
"""

from datetime import date, timedelta

from pawpal_system import Owner, Pet, Scheduler, Task


# --- Helpers --------------------------------------------------------------

def _owner_with_pet():
    """Return an (owner, pet) pair with the pet already attached."""
    owner = Owner(name="Alex")
    pet = Pet(name="Biscuit", species="Dog")
    owner.add_pet(pet)
    return owner, pet


# --- Basic behaviors ------------------------------------------------------

def test_mark_complete_changes_status():
    """Calling mark_complete() should flip the task's completed flag."""
    task = Task(description="Morning walk", time="08:00")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Adding a task to a pet should increase that pet's task count."""
    pet = Pet(name="Biscuit", species="Dog")
    assert pet.task_count() == 0
    pet.add_task(Task(description="Feeding", time="09:00"))
    assert pet.task_count() == 1


# --- Sorting correctness --------------------------------------------------

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order should come back sorted by time."""
    owner, pet = _owner_with_pet()
    pet.add_task(Task(description="Evening", time="18:00"))
    pet.add_task(Task(description="Morning", time="08:00"))
    pet.add_task(Task(description="Midday", time="12:00"))

    times = [task.time for _, task in Scheduler(owner).sort_by_time()]
    assert times == ["08:00", "12:00", "18:00"]


# --- Recurrence logic -----------------------------------------------------

def test_completing_daily_task_creates_next_day_instance():
    """Completing a daily task should queue a fresh task due tomorrow."""
    owner, pet = _owner_with_pet()
    today = date.today().isoformat()
    task = Task(description="Walk", time="08:00", frequency="daily", due_date=today)
    pet.add_task(task)

    upcoming = Scheduler(owner).complete_task(pet, task)

    assert task.completed is True
    assert upcoming is not None
    assert upcoming.completed is False
    assert upcoming.due_date == (date.today() + timedelta(days=1)).isoformat()
    assert pet.task_count() == 2  # original + next occurrence


def test_completing_one_off_task_creates_no_new_task():
    """A non-recurring task should not spawn a follow-up."""
    owner, pet = _owner_with_pet()
    task = Task(description="Vet visit", time="10:00", frequency="once")
    pet.add_task(task)

    upcoming = Scheduler(owner).complete_task(pet, task)

    assert upcoming is None
    assert pet.task_count() == 1


# --- Conflict detection ---------------------------------------------------

def test_detect_conflicts_flags_duplicate_times():
    """Two tasks at the same time should produce one conflict warning."""
    owner, pet = _owner_with_pet()
    pet.add_task(Task(description="Walk", time="08:00"))
    pet.add_task(Task(description="Feeding", time="08:00"))

    conflicts = Scheduler(owner).detect_conflicts()
    assert len(conflicts) == 1
    assert "08:00" in conflicts[0]


def test_no_conflict_when_times_differ():
    """Distinct times should produce no conflict warnings."""
    owner, pet = _owner_with_pet()
    pet.add_task(Task(description="Walk", time="08:00"))
    pet.add_task(Task(description="Feeding", time="09:00"))

    assert Scheduler(owner).detect_conflicts() == []


# --- Edge cases -----------------------------------------------------------

def test_empty_pet_has_no_tasks_or_conflicts():
    """A pet with no tasks should sort/conflict cleanly without errors."""
    owner, _pet = _owner_with_pet()
    scheduler = Scheduler(owner)
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []


def test_filter_by_pet_returns_only_that_pets_tasks():
    """Filtering by pet name should exclude other pets' tasks."""
    owner, biscuit = _owner_with_pet()
    mittens = Pet(name="Mittens", species="Cat")
    owner.add_pet(mittens)
    biscuit.add_task(Task(description="Walk", time="08:00"))
    mittens.add_task(Task(description="Litter", time="09:00"))

    biscuit_tasks = Scheduler(owner).filter_by_pet("Biscuit")
    assert len(biscuit_tasks) == 1
    assert biscuit_tasks[0].description == "Walk"
