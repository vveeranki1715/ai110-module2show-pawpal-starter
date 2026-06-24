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

My conflict detection (`Scheduler.detect_conflicts()`) only flags tasks that share the **exact same start time** (e.g., two tasks both at "08:00"). It does **not** account for overlapping durations — a 30-minute walk starting at 08:00 and a feeding at 08:15 won't be reported as a conflict, even though they physically overlap.

This tradeoff is reasonable for the scenario: a pet owner's plan is a lightweight daily checklist, not a minute-accurate calendar. Exact-time matching catches the most common and most obvious double-bookings while keeping the logic simple, fast, and easy to reason about. It returns warning strings rather than raising, so the app keeps running. If the app later needed true calendar behavior, I'd extend it to compare `time + duration` ranges for overlap — but that adds parsing and interval-math complexity that isn't justified yet.

---

## 3. AI Collaboration

**a. How you used AI**

I used my AI coding assistant across every phase but for different jobs:

- **Design brainstorming** — generating the first Mermaid UML diagram from my brainstormed classes, attributes, and methods.
- **Scaffolding** — turning the UML into dataclass skeletons with empty method stubs (agent/multi-file editing was most effective here).
- **Algorithm help** — asking targeted questions like "how do I sort 'HH:MM' strings with a `sorted()` lambda key?" and "how do I use `timedelta` to compute the next occurrence date?"
- **Testing** — drafting a test plan ("what edge cases matter for a scheduler with sorting and recurring tasks?") and then the test functions.
- **Debugging/refactoring** — reviewing methods for readability and missing relationships.

The most helpful prompts were **specific and scoped** ("sort these objects by this attribute") rather than open-ended ("write my scheduler"). Attaching the actual file so the assistant could see my real class names made its suggestions drop in cleanly.

**Most effective features:** inline/agent multi-file editing for scaffolding, and chat for narrow algorithm questions and explaining unfamiliar code before I saved it.

**b. Judgment and verification**

**One suggestion I modified:** the assistant initially proposed storing `priority` as a free-text string and re-mapping it to a rank inside the sort. I kept the string for readability but added a small `PRIORITY_RANK` constant and a `Task.priority_rank()` helper, so the mapping lives in one place instead of being duplicated in every sort call. I also rejected an early suggestion to keep a separate `Plan` class — once `Scheduler` produced formatted output directly, the extra class added complexity without value, so I removed it from the final UML.

**How I verified suggestions:** I ran `python main.py` to eyeball behavior (e.g., confirming out-of-order tasks actually reordered and the next-occurrence date was today + 1), and I relied on `python -m pytest` — when a behavior mattered, I wrote a test that asserted it rather than trusting the code by inspection.

---

## 3.5. AI Strategy

**Which AI features were most effective:** Agent/multi-file editing was best for repetitive scaffolding (generating all four class skeletons at once). Scoped chat questions were best for the algorithmic pieces — `timedelta` recurrence and the `sorted()` lambda key — because I could ask, understand, and verify one idea at a time.

**An AI suggestion I rejected/modified:** I declined the separate `Plan` class the assistant suggested in the initial design. After implementing `Scheduler.format_schedule()`, a `Plan` object would have just wrapped a list I was already producing, so I folded it in to keep the architecture clean — and updated `uml_final.mmd` to match.

**How separate chat sessions helped:** Using a fresh session per phase (design, implementation, algorithms, testing) kept each conversation focused on one concern. The testing session wasn't polluted with implementation back-and-forth, so its edge-case suggestions were sharper, and I could attach only the files relevant to that phase.

**What I learned as "lead architect":** The AI is fast at producing plausible code, but it doesn't own the design — I do. My job was to set the structure (UML, class responsibilities), ask precise questions, and **verify every suggestion against running code and tests** before accepting it. The best results came from treating the assistant as a knowledgeable pair-programmer whose output I always reviewed, not as an autopilot.

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
