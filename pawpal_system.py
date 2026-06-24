"""PawPal+ logic layer.

Backend classes for the pet-care planning system. These are skeletons
generated from the UML draft (diagrams/uml_draft.mmd) — attributes and
empty method stubs only; scheduling logic comes in a later phase.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Owner:
    """The person responsible for the pet."""

    name: str
    preferences: dict = field(default_factory=dict)
    available_minutes: int = 0

    def set_preferences(self, preferences: dict) -> None:
        """Update the owner's care preferences."""
        raise NotImplementedError

    def set_time_budget(self, minutes: int) -> None:
        """Set how many minutes the owner has available today."""
        raise NotImplementedError


@dataclass
class Pet:
    """The animal being cared for."""

    name: str
    species: str
    breed: str = ""
    age: int = 0
    notes: str = ""

    def update_info(self, **kwargs) -> None:
        """Update one or more pet attributes."""
        raise NotImplementedError

    def describe(self) -> str:
        """Return a human-readable description of the pet."""
        raise NotImplementedError


@dataclass
class Task:
    """A single pet-care activity."""

    name: str
    category: str
    duration: int
    priority: str = "medium"
    recurrence: str = "daily"
    preferred_time: str | None = None
    done: bool = False

    def mark_done(self) -> None:
        """Mark this task as completed."""
        raise NotImplementedError

    def edit(self, **kwargs) -> None:
        """Edit one or more task attributes."""
        raise NotImplementedError

    def is_recurring(self) -> bool:
        """Return True if the task repeats (daily/weekly)."""
        raise NotImplementedError


@dataclass
class Plan:
    """The generated daily schedule produced by the Scheduler."""

    date: str
    scheduled_items: list = field(default_factory=list)
    skipped_tasks: list[Task] = field(default_factory=list)
    total_time: int = 0
    reasoning: str = ""

    def add_item(self, task: Task, time: str) -> None:
        """Add a task to the plan at the given time slot."""
        raise NotImplementedError

    def summary(self) -> str:
        """Return a short summary of the plan."""
        raise NotImplementedError

    def to_display(self) -> str:
        """Return a formatted, user-facing view of the plan."""
        raise NotImplementedError


class Scheduler:
    """The engine that turns tasks + constraints into a daily Plan."""

    def __init__(self, tasks: list[Task] | None = None,
                 time_budget: int = 0, preferences: dict | None = None):
        self.tasks: list[Task] = tasks or []
        self.time_budget = time_budget
        self.preferences = preferences or {}

    def sort_tasks(self) -> list[Task]:
        """Order tasks by priority (and duration as a tiebreaker)."""
        raise NotImplementedError

    def filter_tasks(self) -> list[Task]:
        """Drop tasks that won't fit within the time budget."""
        raise NotImplementedError

    def resolve_conflicts(self) -> None:
        """Handle overlapping or conflicting time slots."""
        raise NotImplementedError

    def generate_plan(self) -> Plan:
        """Build and return a daily Plan from the tasks and constraints."""
        raise NotImplementedError

    def explain_plan(self) -> str:
        """Explain why the scheduler produced the plan it did."""
        raise NotImplementedError
