# 🚀 Productivity Suite (To-Do + Pomodoro + Notes + Calendar)

A modern **productivity desktop app** built with **Python (PyQt5)**.  
It combines a **To-Do Manager**, **Pomodoro Timer**, **Quick Notes**, and a **Calendar with daily notes**, all inside a clean, modern UI with **dark/light mode toggle**.

---

## ✨ Features

- **📝 To-Do Manager**
  - Add, delete, check/uncheck tasks
  - Sort by newest
  - Clear completed tasks
  - Persistent storage

- **⏱ Pomodoro Timer**
  - Work, short break, long break durations (configurable)
  - Auto-cycle option (work → break → work …)
  - Alerts when a session finishes

- **📒 Notes**
  - Quick notes section with autosave
  - Manual save button

- **📅 Calendar**
  - Month view
  - Add notes to specific dates
  - Save / delete notes for each day

- **🌙☀ Dark/Light Mode**
  - Toggle between modern dark and light themes

- **💾 Persistent Data**
  - All tasks, notes, and settings are saved to:
    ```
    C:\Users\25G500011\Projects\todo-pomo\data.json
    ```

---

## 📦 Installation

### 1. Clone / Copy the Project
```bash
cd C:\Users\25G500011\Projects
mkdir todo-pomo
cd todo-pomo
````

Place the main Python file (e.g., `productivity_suite.py`) inside this folder.

### 2. Install Dependencies

This app uses **PyQt5** only:

```bash
pip install PyQt5
```

### 3. Run the App

```bash
python productivity_suite.py
```

---

## 🗂 Project Structure

```
todo-pomo/
│
├── productivity_suite.py   # Main application
├── data.json               # Saved tasks, notes, and settings (auto-created)
└── README.md               # This documentation
```

---

## 🎮 Usage Tips

* **Add a task:** Type in the box and press **Enter** or click **Add Task**
* **Mark task done:** Double-click it
* **Switch themes:** Click the **🌙 Dark Mode / ☀ Light Mode** button
* **Start Pomodoro:** Click **▶ Start**, adjust durations with spinners
* **Calendar notes:** Click a date → type note → save

---

## 📌 Notes

* Your data is always stored locally in `data.json`
* If the file gets corrupted, you can delete it — the app will create a new one
* Designed for **Windows 10/11**, but works on Linux/macOS as well

---

## 🛠 Tech Stack

* **Language:** Python 3.8+
* **UI Framework:** PyQt5
* **Storage:** Local JSON

---

## 📜 License

MIT License. Free to use, modify, and share.
