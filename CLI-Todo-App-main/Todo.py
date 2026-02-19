import json
import os

# File to store tasks
TASKS_FILE = "tasks.json"

def load_tasks():
    """Load tasks from the JSON file."""
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks):
    """Save tasks to the JSON file."""
    with open (TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)


def list_tasks(tasks):
    """Display all tasks with staus."""
    if not tasks:
        print("\n✅ No tasks found!\n")
        return
    print("\n📋 To=Do List:")
    for i, task in enumerate(tasks, start=1):
        status = "✔" if task["done"] else "✘"
        print(f"{i}. {task['title']} [{status}]")
    print()


def add_task(tasks):
    """Add a new task."""
    title = input("Enter task: ").strip()
    if title:
        tasks.append({"title": title, "done": False})
        save_tasks(tasks)
        print("✅ Task added!\n")
    else:
        print("⚠️ Task cannot be empty.\n")


def complete_tasks(tasks):
    """Mark a task as completed."""
    list_tasks(tasks)
    try:
        choice = int(input("Enter task number to complete: "))
        tasks[choice - 1]["done"] =  True
        save_tasks(tasks)
        print("✅ Task marked as complete!\n")
    except (ValueError, IndexError):
        print("⚠️ Invalid task number.\n")


def delete_tasks(tasks):
    """Delete a taks."""
    list_tasks(tasks)
    try:
        choice = int(input("Enter task number to delete: "))
        removed = tasks.pop(choice - 1)
        save_tasks(tasks)
        print(f"🗑️ Task '{removed['title']}' deleted!\n")
    except (ValueError, IndexError):
        print("⚠️ Invalid task number.\n")


def main():
    """Main CLI Loop"""
    tasks = load_tasks()
    while True:
        print("=== CLI To-Do App ===")
        print("1. List tasks")
        print("2. Add task")
        print("3. Complete task")
        print("4. Delete task")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == "1":
            list_tasks(tasks)
        elif choice == "2":
            add_task(tasks)
        elif choice == "3":
            complete_tasks(tasks)
        elif choice == "4":
            delete_tasks(tasks)
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice.\n")

if __name__ == "__main__":
    main()