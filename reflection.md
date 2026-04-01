# PawPal+ Project Reflection

## 1. System Design

PawPal+ is a smart planner for people with pet. It allow the use to input a list of tasks such walking their pet, going to the vet, feeding, etc and the program will output a daily plan that will account for the user availability and time preferences. The program will also explain its reasoning for its plan.
**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

Task — Represents a single pet care activity with attributes like description, duration, priority, frequency, and due date. Provides methods to mark it complete and check whether it is overdue or due today.

Pet — Stores a pet's profile (name, species, breed, age) along with a list of associated Task objects. Provides methods to add, remove, modify, and list its tasks.

Owner — Holds an owner's name, email, and daily available time budget, plus a collection of their Pet objects. Provides methods to add, remove, and list pets, as well as retrieve all tasks across every pet.

Scheduler — Takes an Owner and uses their available time and pets' tasks to generate an ordered daily care plan. Provides methods to filter and sort tasks by priority and to return human-readable reasoning behind the schedule.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The Task priority attribute now store a Priority Enum rather than a string so that it will be less like for me to cause a bug during programming due to incosistent casing or typo when setting task priority.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler consider time and priority constraints. It priorize task that are due today and then focuses on task that arehigh priority.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One of my scheduler it sort task sequentially. This make the scheduling logic a lot simpler, ensure no overlapping conflict, and works better for the user since the scheduler doesn't know other non-pet related tasks in the user schedule.

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
