# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## ✨ Features

- **Multi-pet management** — one owner can track multiple pets, each with its own list of care tasks.
- **Sorting by time** — `Scheduler.sort_by_time()` orders all tasks chronologically by their "HH:MM" time, using priority (high first) to break ties.
- **Filtering** — view tasks for a single pet (`filter_by_pet`) or by completion status (`filter_by_status`).
- **Daily/weekly recurrence** — completing a recurring task auto-queues a fresh instance for the next date (today + 1 day or + 1 week) via `timedelta`.
- **Conflict warnings** — `detect_conflicts()` flags any two uncompleted tasks scheduled at the same time, returning a warning instead of crashing.
- **Interactive UI** — a Streamlit app to add pets, add tasks, and generate a sorted daily schedule with conflict alerts.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

Output from running `python main.py`:

```
Today's Schedule for Alex
================================
  08:00  [    ] Morning walk (30 min)  -> Biscuit [high]
  08:00  [    ] Litter cleanup (10 min)  -> Mittens [low]
  09:00  [    ] Feeding (10 min)  -> Mittens [medium]
  18:00  [    ] Evening walk (30 min)  -> Biscuit [high]

⚠️  Conflict at 08:00: Morning walk (Biscuit), Litter cleanup (Mittens)
```

## 🧪 Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

**What the tests cover** (`tests/test_pawpal.py`):

- **Basics** — `mark_complete()` flips a task's status; adding a task increases a pet's task count.
- **Sorting correctness** — tasks added out of order come back in chronological order.
- **Recurrence logic** — completing a daily task queues a fresh, uncompleted task due the following day; a one-off task spawns no follow-up.
- **Conflict detection** — two tasks at the same time produce exactly one warning; distinct times produce none.
- **Edge cases** — a pet with no tasks sorts/conflict-checks cleanly; filtering by pet name excludes other pets' tasks.

Successful test run:

```
collected 9 items

tests/test_pawpal.py .........                                           [100%]

============================== 9 passed in 0.02s ===============================
```

**Confidence level: ★★★★☆ (4/5)** — All core behaviors (sorting, recurrence, conflict detection) and key edge cases pass. Held at 4 because conflict detection only checks exact start times (not overlapping durations), and recurrence hasn't been tested across month/year boundaries.

## 📐 Smarter Scheduling

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_by_time()` | Sorts (pet, task) pairs by the "HH:MM" time string; priority (high first) breaks ties; untimed tasks sort last. |
| Filtering | `Scheduler.filter_by_pet(name)`, `Scheduler.filter_by_status(completed)` | Filter tasks down to a single pet, or to completed vs. incomplete. |
| Conflict detection | `Scheduler.detect_conflicts()` | Lightweight check — warns (doesn't crash) when two uncompleted tasks share the exact same start time. |
| Recurring tasks | `Task.next_occurrence()`, `Scheduler.complete_task(pet, task)` | Completing a daily/weekly task uses `timedelta` to queue a fresh instance on the next date (today + 1 day / + 1 week). |

## 📸 Demo Walkthrough

Launch the interactive app with `streamlit run app.py`.

**Main UI features & actions:**
- **Owner** — set the owner's name.
- **Add a Pet** — submit a pet's name, species, and breed; the form calls `Owner.add_pet()`.
- **Add a Task** — pick a pet, then enter a task title, time, duration, and priority; the form calls `Pet.add_task()`.
- **Current Pets & Tasks** — each pet's tasks are listed in a table with their status.
- **Generate Schedule** — builds a `Scheduler`, shows conflict warnings (`st.warning`) or a success banner, then renders the time-sorted plan as a table.

**Example workflow:**
1. Set the owner name to *Alex*.
2. Add a pet — *Biscuit* (Dog, Golden Retriever).
3. Add a second pet — *Mittens* (Cat, Tabby).
4. Add tasks: Biscuit → "Morning walk" at 08:00 and "Evening walk" at 18:00; Mittens → "Litter cleanup" at 08:00 and "Feeding" at 09:00.
5. Click **Generate schedule** → tasks appear sorted by time, and an 08:00 conflict warning is shown between Biscuit's walk and Mittens' litter cleanup.

**Key Scheduler behaviors shown:** chronological **sorting** (out-of-order tasks reorder), **conflict warnings** (duplicate 08:00 slot flagged), per-pet **task lists**, and **recurrence** (completing a daily task queues tomorrow's instance — visible in the CLI demo).

**Sample CLI output** (`python main.py`):

```
Today's Schedule for Alex
================================
  08:00  [    ] Morning walk (30 min)  -> Biscuit [high]
  08:00  [    ] Litter cleanup (10 min)  -> Mittens [low]
  09:00  [    ] Feeding (10 min)  -> Mittens [medium]
  18:00  [    ] Evening walk (30 min)  -> Biscuit [high]

⚠️  Conflict at 08:00: Morning walk (Biscuit), Litter cleanup (Mittens)

Biscuit's tasks only:
  18:00  Evening walk
  08:00  Morning walk

Completed 'Morning walk' -> next occurrence due 2026-06-24
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->
