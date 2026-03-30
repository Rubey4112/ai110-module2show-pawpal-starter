# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PawPal+** is a Python/Streamlit app for pet care task planning. The project is a starter skeleton — the UI shell exists in `app.py`, but the backend domain logic (classes and scheduling) must be designed and implemented by the student.

## Commands

```bash
# Set up environment (one-time)
python -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run the app
streamlit run app.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_scheduler.py

# Run a specific test
pytest tests/test_scheduler.py::test_function_name
```

## Architecture

The intended architecture has four domain classes (to be built):

- **`Owner`** — holds owner info and a list of `Pet` objects; methods to add/remove/list pets
- **`Pet`** — holds name, species, and a list of `Task` objects; methods to add/modify/list tasks
- **`Task`** — holds description, duration, priority, due date, and completion status; has a `mark_complete()` method
- **`Scheduler`** — aggregates tasks across all pets for an owner, applies scheduling logic (time constraints, priority ordering), and produces an ordered daily plan with reasoning

**Current state**: `app.py` is UI-only. It uses `st.session_state.tasks` as a plain list of dicts. Once the domain classes exist, the UI should instantiate them and call `Scheduler` to generate and display the plan.

**Integration point**: The `"Generate schedule"` button handler at the bottom of `app.py` is where the `Scheduler` output should be rendered.

## Constraints

- `requirements.txt` specifies only `streamlit>=1.30` and `pytest>=7.0`. Add packages there if needed.
- Tests go in a `tests/` directory (create it if absent); use `pytest` conventions.
- `reflection.md` and `class_structure.md` are coursework submission documents — do not modify their structure.
