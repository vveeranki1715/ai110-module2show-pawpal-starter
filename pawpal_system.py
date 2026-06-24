"""PawPal+ logic layer.

Backend classes for the pet-care planning system. Implemented from the
UML draft (diagrams/uml_draft.mmd):

- Task      -> a single care activity
- Pet       -> pet details + its list of tasks
- Owner     -> manages multiple pets, exposes all their tasks
- Scheduler -> organizes tasks across the owner's pets into a daily plan
"""

from __future__ import annotations

from dataclasses import dataclass, field

# Priority rank used for sorting (higher = more important).
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, etc.)."""

    description: str
    time: str = ""
    duration: int = 0
    priority: str = "medium"
    frequency: str = "daily"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task back to not completed."""
        self.completed = False

    def is_recurring(self) -> bool:
        """Return True if the task repeats rather than being one-off."""
        return self.frequency.lower() in {"daily", "weekly"}

    def priority_rank(self) -> int:
        """Return the numeric sort rank for this task's priority."""
        return PRIORITY_RANK.get(self.priority.lower(), 0)


@dataclass
class Pet:
    """A pet, including its details and its list of care tasks."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    notes: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a care task from this pet if present."""
        if task in self.tasks:
            self.tasks.remove(task)

    def task_count(self) -> int:
        """Return how many tasks this pet currently has."""
        return len(self.tasks)

    def describe(self) -> str:
        """Return a human-readable description of the pet."""
        breed = f" {self.breed}" if self.breed else ""
        return f"{self.name} ({self.species}{breed})"


@dataclass
class Owner:
    """The person responsible for one or more pets."""

    name: str
    preferences: dict = field(default_factory=dict)
    available_minutes: int = 0
    pets: list[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner."""
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all of the owner's pets."""
        return [task for pet in self.pets for task in pet.tasks]

    def get_tasks_with_pets(self) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs across all pets, preserving ownership."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def set_time_budget(self, minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        self.available_minutes = minutes


class Scheduler:
    """The engine that organizes tasks across an owner's pets into a plan."""

    def __init__(self, owner: Owner):
        """Create a scheduler bound to a specific owner."""
        self.owner = owner

    def get_tasks(self) -> list[tuple[Pet, Task]]:
        """Retrieve all (pet, task) pairs from the owner's pets."""
        return self.owner.get_tasks_with_pets()

    def sort_tasks(self) -> list[tuple[Pet, Task]]:
        """Order tasks by scheduled time, then by priority (high first)."""
        pairs = self.get_tasks()
        return sorted(
            pairs,
            key=lambda pt: (pt[1].time or "99:99", -pt[1].priority_rank()),
        )

    def todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return today's recurring/daily tasks in scheduled order."""
        return [pt for pt in self.sort_tasks() if pt[1].is_recurring()]

    def format_schedule(self) -> str:
        """Return a clean, readable 'Today's Schedule' string for the terminal."""
        lines = [f"Today's Schedule for {self.owner.name}", "=" * 32]
        schedule = self.sort_tasks()
        if not schedule:
            lines.append("  (no tasks scheduled)")
            return "\n".join(lines)
        for pet, task in schedule:
            time = task.time or "  --  "
            status = "[done]" if task.completed else "[    ]"
            dur = f" ({task.duration} min)" if task.duration else ""
            lines.append(
                f"  {time}  {status} {task.description}{dur}"
                f"  -> {pet.name} [{task.priority}]"
            )
        return "\n".join(lines)
