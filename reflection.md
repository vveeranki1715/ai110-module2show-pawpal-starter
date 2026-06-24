# PawPal+ Project Reflection

## 1. System Design

**Core user actions**

Three core actions a user should be able to perform in PawPal+:

1. **Add a pet and owner profile** — The user enters basic owner info and their pet's details (name, type/breed) so the assistant knows who it is planning care for.
2. **Add and manage care tasks** — The user adds, edits, or removes pet care tasks (walks, feeding, meds, grooming, enrichment), each with at least a duration and a priority level.
3. **Generate and view a daily plan** — The user requests a daily schedule, and the app produces a clear, ordered plan based on the available time, task priorities, and preferences — ideally explaining why it chose that arrangement.

**Building blocks (objects)**

The main objects needed for the system, with the information they hold (attributes) and actions they perform (methods):

**`Owner`** — the person responsible for the pet.
- *Attributes:* `name`, `preferences` (e.g., preferred walk times, quiet hours), `available_minutes` (time budget for the day).
- *Methods:* `set_preferences()`, `set_time_budget(minutes)`.

**`Pet`** — the animal being cared for.
- *Attributes:* `name`, `species`, `breed`, `age`, `notes` (e.g., dietary or medical needs).
- *Methods:* `update_info()`, `describe()`.

**`Task`** — a single care activity.
- *Attributes:* `name`, `category` (walk/feeding/meds/grooming/enrichment), `duration` (minutes), `priority` (high/medium/low), `recurrence` (daily/weekly), `preferred_time` (optional).
- *Methods:* `mark_done()`, `edit(...)`, `is_recurring()`.

**`Scheduler`** — the engine that turns tasks + constraints into a plan.
- *Attributes:* `tasks` (list), `time_budget`, `preferences`.
- *Methods:* `sort_tasks()` (by priority/duration), `filter_tasks()` (drop tasks that won't fit), `resolve_conflicts()` (overlapping slots), `generate_plan()`, `explain_plan()`.

**`Plan`** — the generated daily schedule (output of the Scheduler).
- *Attributes:* `date`, `scheduled_items` (ordered task + time-slot pairs), `skipped_tasks`, `total_time`, `reasoning`.
- *Methods:* `add_item(task, time)`, `summary()`, `to_display()`.

**a. Initial design**

My initial UML design used five classes, split between data holders and logic:

- **`Owner`** — holds the person's name, care preferences, and daily time budget. Responsible for owning pets and supplying the constraints the scheduler works within.
- **`Pet`** — holds identifying info (name, species, breed, age) and care notes. A passive data object describing who is being cared for.
- **`Task`** — holds a single care activity's name, category, duration, priority, and recurrence. Represents the unit of work to be scheduled.
- **`Scheduler`** — the logic engine. Responsible for sorting, filtering, and resolving conflicts among tasks, then generating and explaining a daily plan.
- **`Plan`** — holds the generated schedule (ordered items, skipped tasks, reasoning). Responsible for presenting the result to the user.

The key design choice was keeping `Owner`/`Pet`/`Task` as pure data holders and concentrating all behavior in `Scheduler`, with `Plan` as its output, so the logic lives in one place.

**b. Design changes**

After asking my AI assistant to review `pawpal_system.py`, I made two changes based on its feedback about missing relationships:

1. **Added `pets: list[Pet]` to `Owner`.** The UML showed "Owner owns many Pets," but the skeleton had no field linking them. Without it the owner couldn't actually hold their pets, so the relationship existed only on paper.
2. **Added `pet_name: str` to `Task`.** Tasks had no way to indicate which pet they belonged to, so a multi-pet household couldn't tell whose walk or feeding a task was. Adding a reference restores that link.

The assistant also flagged a potential bottleneck: `priority` is stored as free text (`"high"/"medium"/"low"`), which forces the scheduler to re-map strings to a sortable rank on every sort. I left this as-is for the skeleton phase but noted it — if it becomes a problem during implementation, I'll switch to an `Enum` or numeric rank.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
