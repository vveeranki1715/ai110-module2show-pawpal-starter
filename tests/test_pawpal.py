"""Quick tests for core PawPal+ behaviors."""

from pawpal_system import Owner, Pet, Task


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
