# CLI To-Do App

A small, dependency-free command-line to-do application written in Python. It provides basic task management — add, list, complete, and delete — while persisting tasks to a JSON file (`tasks.json`). Ideal as a learning example or a tiny utility for personal use.

---

## Features

* List tasks with status (done / not done)
* Add new tasks
* Mark tasks as completed
* Delete tasks
* Persist tasks to `tasks.json` (human readable, editable)

---

## Requirements

* Python 3.8+ (should work on 3.7, but 3.8+ recommended)
* No third-party dependencies

---

## Files

* `todo.py` — main program (replace with your filename if different)
* `tasks.json` — created automatically in the same folder to store tasks

---

## Installation

1. Clone or copy the script to a directory:

```bash
git clone <your-repo-url>
cd <your-repo-folder>
```

2. (Optional) Create a virtual environment:

```bash
python -m venv .venv
# Activate:
# macOS / Linux: source .venv/bin/activate
# Windows (PowerShell): .\.venv\Scripts\Activate.ps1
```

3. There are no dependencies to install.

---

## Usage

Run the script with Python from the directory containing the file:

```bash
python todo.py
```

You will see the menu:

```
=== CLI To-Do App ===
1. List tasks
2. Add task
3. Complete task
4. Delete task
5. Exit
Choose an option: 
```

Example session:

```
Choose an option: 2
Enter task: Buy groceries
✅ Task added!

Choose an option: 1

📋 To-Do List:
1. Buy groceries [✘]
```

Tasks persist between runs in `tasks.json`.

---

## Data format

`tasks.json` stores a simple list of objects. Example:

```json
[
    {
        "title": "Buy groceries",
        "done": false
    },
    {
        "title": "Read documentation",
        "done": true
    }
]
```

You may edit this file manually if required, but ensure the JSON structure remains valid.

---

## Configuration

* The file used to store tasks is defined by the `TASKS_FILE` constant at the top of the script. Change it if you want to store tasks in a different location or filename.

```python
TASKS_FILE = "tasks.json"  # change as needed
```

---

## Suggested Improvements

If you want to extend the program, here are ideas:

* Add due dates and sorting/filtering by date or status
* Add priorities and search
* Add command-line arguments (e.g., `todo.py add "Task name"`)
* Add unit tests and input validation
* Add concurrency-safe file access (file locking)
* Replace JSON with SQLite for richer queries

---

## Troubleshooting

* If the app crashes when completing or deleting a task, ensure you entered a valid task number.
* If `tasks.json` is malformed (manual edit error), delete or fix it — the app will recreate a new `tasks.json` when needed.
* Ensure you run the script from the directory containing the script (or use full paths).

---

## Contributing

Contributions are welcome. Suggested workflow:

1. Fork the repo
2. Create a branch for your feature/fix
3. Open a pull request with a short description and tests (if applicable)
