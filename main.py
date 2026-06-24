"""Temporary demo script to verify the PawPal+ logic layer in the terminal.

Run with: python main.py
"""

from pawpal_system import Owner, Pet, Scheduler, Task


def main() -> None:
    # Create an owner with two pets.
    owner = Owner(name="Alex", available_minutes=120)

    biscuit = Pet(name="Biscuit", species="Dog", breed="Golden Retriever", age=4)
    mittens = Pet(name="Mittens", species="Cat", breed="Tabby", age=2)
    owner.add_pet(biscuit)
    owner.add_pet(mittens)

    # Add tasks OUT OF ORDER on purpose to prove sorting works.
    biscuit.add_task(Task(description="Evening walk", time="18:00", duration=30, priority="high"))
    biscuit.add_task(Task(description="Morning walk", time="08:00", duration=30, priority="high"))
    mittens.add_task(Task(description="Feeding", time="09:00", duration=10, priority="medium"))
    # Same time as Biscuit's morning walk -> conflict.
    mittens.add_task(Task(description="Litter cleanup", time="08:00", duration=10, priority="low"))

    scheduler = Scheduler(owner)

    # Sorting by time.
    print(scheduler.format_schedule())

    # Filtering by pet.
    print("\nBiscuit's tasks only:")
    for task in scheduler.filter_by_pet("Biscuit"):
        print(f"  {task.time}  {task.description}")

    # Recurring task: completing the morning walk queues tomorrow's instance.
    morning = next(t for t in biscuit.tasks if t.description == "Morning walk")
    upcoming = scheduler.complete_task(biscuit, morning)
    print(f"\nCompleted 'Morning walk' -> next occurrence due {upcoming.due_date}")

    # Filtering by status.
    print("\nRemaining (incomplete) tasks:")
    for pet, task in scheduler.filter_by_status(completed=False):
        print(f"  {task.time}  {task.description} ({pet.name})")


if __name__ == "__main__":
    main()
