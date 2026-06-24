"""PawPal+ logic layer.

Backend classes for the pet-care planning system. Implemented from the
UML draft (diagrams/uml_draft.mmd):

- Task      -> a single care activity
- Pet       -> pet details + its list of tasks
- Owner     -> manages multiple pets, exposes all their tasks
- Scheduler -> sorts, filters, regenerates, and conflict-checks tasks
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta

# Priority rank used for sorting (higher = more important).
PRIORITY_RANK = {"high": 3, "medium": 2, "low": 1}

# How far ahead the next occurrence of a recurring task lands.
RECURRENCE_DELTA = {"daily": timedelta(days=1), "weekly": timedelta(weeks=1)}


@dataclass
class Task:
    """A single pet-care activity (walk, feeding, meds, etc.)."""

    description: str
    time: str = ""
    duration: int = 0
    priority: str = "medium"
    frequency: str = "daily"
    due_date: str = ""  # ISO date "YYYY-MM-DD"; blank means "no specific date"
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Reset this task back to not completed."""
        self.completed = False

    def is_recurring(self) -> bool:
        """Return True if the task repeats rather than being one-off."""
        return self.frequency.lower() in RECURRENCE_DELTA

    def priority_rank(self) -> int:
        """Return the numeric sort rank for this task's priority."""
        return PRIORITY_RANK.get(self.priority.lower(), 0)

    def next_occurrence(self) -> "Task | None":
        """Return a fresh, uncompleted copy due on the next recurrence date.

        Uses timedelta to advance the due date (today + 1 day for daily,
        + 1 week for weekly). Returns None for non-recurring tasks.
        """
        if not self.is_recurring():
            return None
        base = (
            datetime.strptime(self.due_date, "%Y-%m-%d").date()
            if self.due_date
            else date.today()
        )
        next_date = base + RECURRENCE_DELTA[self.frequency.lower()]
        return Task(
            description=self.description,
            time=self.time,
            duration=self.duration,
            priority=self.priority,
            frequency=self.frequency,
            due_date=next_date.isoformat(),
            completed=False,
        )


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
    """The engine that sorts, filters, and conflict-checks an owner's tasks."""

    def __init__(self, owner: Owner):
        """Create a scheduler bound to a specific owner."""
        self.owner = owner

    def get_tasks(self) -> list[tuple[Pet, Task]]:
        """Retrieve all (pet, task) pairs from the owner's pets."""
        return self.owner.get_tasks_with_pets()

    def sort_by_time(self) -> list[tuple[Pet, Task]]:
        """Sort (pet, task) pairs by the task's "HH:MM" time string.

        Sorting "HH:MM" strings lexically works because zero-padded 24-hour
        times sort the same as chronological order. Tasks with no time sort
        last; priority (high first) breaks ties at the same time.
        """
        return sorted(
            self.get_tasks(),
            key=lambda pt: (pt[1].time or "99:99", -pt[1].priority_rank()),
        )

    def filter_by_pet(self, pet_name: str) -> list[Task]:
        """Return only the tasks belonging to the named pet."""
        return [
            task
            for pet in self.owner.pets
            if pet.name == pet_name
            for task in pet.tasks
        ]

    def filter_by_status(self, completed: bool) -> list[tuple[Pet, Task]]:
        """Return (pet, task) pairs matching the given completion status."""
        return [pt for pt in self.get_tasks() if pt[1].completed == completed]

    def complete_task(self, pet: Pet, task: Task) -> "Task | None":
        """Mark a task complete and, if recurring, queue its next occurrence.

        Returns the newly created next-occurrence Task, or None if the task
        was one-off.
        """
        task.mark_complete()
        upcoming = task.next_occurrence()
        if upcoming is not None:
            pet.add_task(upcoming)
        return upcoming

    def detect_conflicts(self) -> list[str]:
        """Return warning strings for tasks that share the same time slot.

        Lightweight check: groups uncompleted tasks by their "HH:MM" time and
        warns on any slot with more than one task. It compares exact start
        times only (not overlapping durations) and never raises.
        """
        by_time: dict[str, list[tuple[Pet, Task]]] = {}
        for pet, task in self.get_tasks():
            if task.completed or not task.time:
                continue
            by_time.setdefault(task.time, []).append((pet, task))

        warnings = []
        for time_slot, pairs in sorted(by_time.items()):
            if len(pairs) > 1:
                labels = ", ".join(f"{t.description} ({p.name})" for p, t in pairs)
                warnings.append(f"⚠️  Conflict at {time_slot}: {labels}")
        return warnings

    def format_schedule(self) -> str:
        """Return a clean, readable 'Today's Schedule' string for the terminal."""
        lines = [f"Today's Schedule for {self.owner.name}", "=" * 32]
        schedule = self.sort_by_time()
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
        conflicts = self.detect_conflicts()
        if conflicts:
            lines.append("")
            lines.extend(conflicts)
        return "\n".join(lines)
