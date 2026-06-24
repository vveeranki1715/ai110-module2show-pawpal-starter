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

    # Add tasks with different times to the pets.
    biscuit.add_task(
        Task(description="Morning walk", time="08:00", duration=30, priority="high")
    )
    biscuit.add_task(
        Task(description="Feeding", time="09:00", duration=10, priority="high")
    )
    mittens.add_task(
        Task(description="Litter cleanup", time="08:30", duration=10, priority="medium")
    )
    mittens.add_task(
        Task(description="Play / enrichment", time="18:00", duration=15, priority="low")
    )

    # Print today's schedule.
    scheduler = Scheduler(owner)
    print(scheduler.format_schedule())


if __name__ == "__main__":
    main()
