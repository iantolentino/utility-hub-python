"""
Productivity Suite (PyQt5)
- To-Do manager with persistent storage
- Pomodoro timer with configurable durations, auto cycle, long break
- Notes pad (global + per-calendar-date) with autosave
- Calendar view (click a date to view/edit its notes)
- Dark / Light mode toggle
- Centered, modern UI

Requirements:
    pip install PyQt5

Run:
    python productivity_suite.py
"""


import sys
import os
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QListWidgetItem, QTextEdit, QTabWidget,
    QCalendarWidget, QSpinBox, QMessageBox, QCheckBox, QGridLayout, QGroupBox
)
from PyQt5.QtCore import Qt, QTimer, QDate
from PyQt5.QtGui import QFont, QIcon

# ---------------------------
# Persistence helpers
# ---------------------------
# Force save path to your project folder
DATA_DIR = r"C:\Users\25G500011\Projects\todo-pomo"
DATA_FILE = os.path.join(DATA_DIR, "data.json")


DEFAULT_DATA = {
    "tasks": [],        # list of {"text": str, "completed": bool, "created": iso}
    "notes": "",        # global notes
    "date_notes": {},   # map "YYYY-MM-DD" -> string
    "settings": {
        "dark_mode": True,
        "pomodoro_work": 25,
        "pomodoro_short": 5,
        "pomodoro_long": 15,
        "long_after": 4
    }
}


def ensure_datafile():
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.isfile(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(DEFAULT_DATA, f, indent=2)


def load_data():
    ensure_datafile()
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return DEFAULT_DATA.copy()


def save_data(data):
    ensure_datafile()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# ---------------------------
# Main Application
# ---------------------------
class ProductivityApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🚀 Productivity Suite")
        self.setWindowIcon(QIcon())  # add an icon path if you want
        self.resize(900, 640)
        self.center_window()

        # Fonts
        self.title_font = QFont("Segoe UI", 18, QFont.Bold)
        self.header_font = QFont("Segoe UI", 12, QFont.Bold)
        self.normal_font = QFont("Segoe UI", 11)

        # Load data
        self.data = load_data()

        # State
        settings = self.data.get("settings", {})
        self.dark_mode = bool(settings.get("dark_mode", True))
        self.pomodoro_mode = "work"  # "work", "short_break", "long_break"
        self.pomo_time_left = 0
        self.pomo_running = False
        self.pomo_cycles_done = 0

        # Build UI
        self.build_ui()

        # Apply theme
        if self.dark_mode:
            self.apply_dark_theme()
            self.theme_btn.setText("🌙 Dark Mode")
        else:
            self.apply_light_theme()
            self.theme_btn.setText("☀ Light Mode")

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.setInterval(1000)  # 1s

        # Load persisted content
        self.load_tasks_into_list()
        self.global_notes.setPlainText(self.data.get("notes", ""))
        self.update_pomodoro_ui(update_time=True)

    def center_window(self):
        screen = QApplication.primaryScreen().availableGeometry()
        size = self.geometry()
        x = (screen.width() - size.width()) // 2
        y = (screen.height() - size.height()) // 2
        self.move(max(x, 0), max(y, 0))

    def build_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Title + theme
        title = QLabel("Productivity Suite")
        title.setFont(self.title_font)
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)

        self.theme_btn = QPushButton()
        self.theme_btn.clicked.connect(self.toggle_theme)
        self.theme_btn.setFixedWidth(140)
        main_layout.addWidget(self.theme_btn, alignment=Qt.AlignCenter)

        # Tabs
        tabs = QTabWidget()
        tabs.setTabPosition(QTabWidget.North)
        tabs.addTab(self.build_todo_tab(), "📝 To-Do")
        tabs.addTab(self.build_pomodoro_tab(), "⏱ Pomodoro")
        tabs.addTab(self.build_notes_tab(), "📒 Notes")
        tabs.addTab(self.build_calendar_tab(), "📅 Calendar")
        main_layout.addWidget(tabs, stretch=1)

        # Footer small controls
        footer = QHBoxLayout()
        footer.setAlignment(Qt.AlignCenter)
        save_btn = QPushButton("💾 Save All")
        save_btn.clicked.connect(self.save_all)
        footer.addWidget(save_btn)
        about_btn = QPushButton("ℹ About")
        about_btn.clicked.connect(self.show_about)
        footer.addWidget(about_btn)
        main_layout.addLayout(footer)

        self.setLayout(main_layout)

    # ---------------------------
    # To-Do Tab
    # ---------------------------
    def build_todo_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        # Input row
        input_row = QHBoxLayout()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("Add a new task and press Enter or Add")
        self.todo_input.returnPressed.connect(self.add_task)
        input_row.addWidget(self.todo_input)

        add_btn = QPushButton("Add Task")
        add_btn.clicked.connect(self.add_task)
        add_btn.setFixedWidth(110)
        input_row.addWidget(add_btn)
        layout.addLayout(input_row)

        # Tasks list
        self.task_list = QListWidget()
        self.task_list.itemDoubleClicked.connect(self.toggle_task_complete)
        layout.addWidget(self.task_list, stretch=1)

        # Actions row
        actions = QHBoxLayout()
        del_btn = QPushButton("🗑 Delete Selected")
        del_btn.clicked.connect(self.delete_task)
        actions.addWidget(del_btn)

        clear_btn = QPushButton("Clear Completed")
        clear_btn.clicked.connect(self.clear_completed)
        actions.addWidget(clear_btn)

        sort_btn = QPushButton("Sort by Newest")
        sort_btn.clicked.connect(self.sort_tasks_newest)
        actions.addWidget(sort_btn)

        layout.addLayout(actions)

        tab.setLayout(layout)
        return tab

    def add_task(self):
        text = self.todo_input.text().strip()
        if not text:
            return
        item = {"text": text, "completed": False, "created": datetime.utcnow().isoformat()}
        self.data.setdefault("tasks", []).append(item)
        self.append_task_item(item)
        self.todo_input.clear()
        save_data(self.data)

    def append_task_item(self, item):
        display = item["text"]
        it = QListWidgetItem(display)
        it.setFont(self.normal_font)
        it.setData(Qt.UserRole, item)
        if item.get("completed"):
            it.setCheckState(Qt.Checked)
            it.setForeground(Qt.gray)
        else:
            it.setCheckState(Qt.Unchecked)
        self.task_list.addItem(it)

    def load_tasks_into_list(self):
        self.task_list.clear()
        for item in self.data.get("tasks", []):
            self.append_task_item(item)

    def toggle_task_complete(self, list_item):
        item = list_item.data(Qt.UserRole)
        item["completed"] = not bool(item.get("completed"))
        # reflect in UI
        if item["completed"]:
            list_item.setForeground(Qt.gray)
            list_item.setCheckState(Qt.Checked)
        else:
            list_item.setForeground(Qt.black)
            list_item.setCheckState(Qt.Unchecked)
        save_data(self.data)

    def delete_task(self):
        sel = self.task_list.currentItem()
        if not sel:
            return
        item = sel.data(Qt.UserRole)
        self.data["tasks"] = [t for t in self.data.get("tasks", []) if t.get("created") != item.get("created")]
        self.load_tasks_into_list()
        save_data(self.data)

    def clear_completed(self):
        self.data["tasks"] = [t for t in self.data.get("tasks", []) if not t.get("completed")]
        self.load_tasks_into_list()
        save_data(self.data)

    def sort_tasks_newest(self):
        self.data["tasks"].sort(key=lambda t: t.get("created", ""), reverse=True)
        self.load_tasks_into_list()
        save_data(self.data)

    # ---------------------------
    # Pomodoro Tab
    # ---------------------------
    def build_pomodoro_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        header = QLabel("Pomodoro Timer")
        header.setFont(self.header_font)
        layout.addWidget(header)

        # Display timer large
        self.pomo_label = QLabel("25:00")
        self.pomo_label.setFont(QFont("Segoe UI", 36, QFont.Bold))
        self.pomo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.pomo_label)

        # Controls (start/pause/reset)
        ctrl = QHBoxLayout()
        self.pomo_start_btn = QPushButton("▶ Start")
        self.pomo_start_btn.clicked.connect(self.toggle_pomodoro)
        ctrl.addWidget(self.pomo_start_btn)

        self.pomo_reset_btn = QPushButton("🔄 Reset")
        self.pomo_reset_btn.clicked.connect(self.reset_pomodoro)
        ctrl.addWidget(self.pomo_reset_btn)

        layout.addLayout(ctrl)

        # Settings group
        settings_box = QGroupBox("Durations (minutes)")
        grid = QGridLayout()

        self.spin_work = QSpinBox(); self.spin_work.setRange(1, 180)
        self.spin_work.setValue(int(self.data.get("settings", {}).get("pomodoro_work", 25)))
        grid.addWidget(QLabel("Work"), 0, 0); grid.addWidget(self.spin_work, 0, 1)

        self.spin_short = QSpinBox(); self.spin_short.setRange(1, 60)
        self.spin_short.setValue(int(self.data.get("settings", {}).get("pomodoro_short", 5)))
        grid.addWidget(QLabel("Short Break"), 1, 0); grid.addWidget(self.spin_short, 1, 1)

        self.spin_long = QSpinBox(); self.spin_long.setRange(1, 60)
        self.spin_long.setValue(int(self.data.get("settings", {}).get("pomodoro_long", 15)))
        grid.addWidget(QLabel("Long Break"), 2, 0); grid.addWidget(self.spin_long, 2, 1)

        self.spin_after = QSpinBox(); self.spin_after.setRange(1, 10)
        self.spin_after.setValue(int(self.data.get("settings", {}).get("long_after", 4)))
        grid.addWidget(QLabel("Long after cycles"), 3, 0); grid.addWidget(self.spin_after, 3, 1)

        settings_box.setLayout(grid)
        layout.addWidget(settings_box)

        # Auto-switch & status
        self.auto_switch_chk = QCheckBox("Auto-switch between work and breaks")
        self.auto_switch_chk.setChecked(True)
        layout.addWidget(self.auto_switch_chk)

        self.pomo_status = QLabel("Status: Idle")
        layout.addWidget(self.pomo_status)

        tab.setLayout(layout)
        return tab

    def toggle_pomodoro(self):
        if self.pomo_running:
            # pause
            self.timer.stop()
            self.pomo_running = False
            self.pomo_start_btn.setText("▶ Start")
            self.pomo_status.setText("Status: Paused")
        else:
            # start or resume
            if self.pomo_time_left <= 0:
                # initialize based on selected mode (start with work)
                self.pomodoro_mode = "work"
                self.pomo_time_left = int(self.spin_work.value()) * 60
                self.pomo_cycles_done = 0
            # update settings in persisted data
            self.data.setdefault("settings", {})["pomodoro_work"] = int(self.spin_work.value())
            self.data["settings"]["pomodoro_short"] = int(self.spin_short.value())
            self.data["settings"]["pomodoro_long"] = int(self.spin_long.value())
            self.data["settings"]["long_after"] = int(self.spin_after.value())
            save_data(self.data)

            self.timer.start()
            self.pomo_running = True
            self.pomo_start_btn.setText("⏸ Pause")
            self.pomo_status.setText(f"Status: {self.pomodoro_mode.title()}")

    def reset_pomodoro(self):
        self.timer.stop()
        self.pomo_running = False
        self.pomo_cycles_done = 0
        self.pomodoro_mode = "work"
        self.pomo_time_left = int(self.spin_work.value()) * 60
        self.update_pomodoro_ui()
        self.pomo_start_btn.setText("▶ Start")
        self.pomo_status.setText("Status: Reset")

    def update_pomodoro_ui(self, update_time=False):
        if update_time and self.pomo_time_left <= 0:
            # initialize if needed
            self.pomo_time_left = int(self.spin_work.value()) * 60
        mins, secs = divmod(max(0, self.pomo_time_left), 60)
        self.pomo_label.setText(f"{mins:02d}:{secs:02d}")

    def tick(self):
        if self.pomo_time_left > 0:
            self.pomo_time_left -= 1
            self.update_pomodoro_ui()
        else:
            # period ended
            self.timer.stop()
            self.pomo_running = False
            # simple alert
            QMessageBox.information(self, "Pomodoro", f"{self.pomodoro_mode.title()} finished!")
            # cycle logic
            if self.pomodoro_mode == "work":
                self.pomo_cycles_done += 1
                # choose long or short break
                if self.pomo_cycles_done % int(self.spin_after.value()) == 0:
                    self.pomodoro_mode = "long_break"
                    self.pomo_time_left = int(self.spin_long.value()) * 60
                else:
                    self.pomodoro_mode = "short_break"
                    self.pomo_time_left = int(self.spin_short.value()) * 60
            else:
                # after break -> work
                self.pomodoro_mode = "work"
                self.pomo_time_left = int(self.spin_work.value()) * 60

            self.update_pomodoro_ui()
            self.pomo_status.setText(f"Status: {self.pomodoro_mode.title()}")
            # auto-switch?
            if self.auto_switch_chk.isChecked():
                self.toggle_pomodoro()  # will start next cycle

    # ---------------------------
    # Notes Tab
    # ---------------------------
    def build_notes_tab(self):
        tab = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        header = QLabel("Quick Notes")
        header.setFont(self.header_font)
        layout.addWidget(header)

        self.global_notes = QTextEdit()
        self.global_notes.setPlaceholderText("Write notes here... (autosaved)")
        self.global_notes.textChanged.connect(self.autosave_notes)
        layout.addWidget(self.global_notes, stretch=1)

        save_btn = QPushButton("Save Notes Now")
        save_btn.clicked.connect(self.save_notes_now)
        layout.addWidget(save_btn)

        tab.setLayout(layout)
        return tab

    def autosave_notes(self):
        # small debounce could be added; simple immediate save for clarity
        self.data["notes"] = self.global_notes.toPlainText()
        save_data(self.data)

    def save_notes_now(self):
        self.data["notes"] = self.global_notes.toPlainText()
        save_data(self.data)
        QMessageBox.information(self, "Notes", "Notes saved.")

    # ---------------------------
    # Calendar Tab
    # ---------------------------
    def build_calendar_tab(self):
        tab = QWidget()
        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignTop)

        left = QVBoxLayout()
        cal_header = QLabel("Calendar")
        cal_header.setFont(self.header_font)
        left.addWidget(cal_header)

        self.calendar = QCalendarWidget()
        self.calendar.clicked.connect(self.on_calendar_date_clicked)
        left.addWidget(self.calendar)

        layout.addLayout(left, 1)

        right = QVBoxLayout()
        rn_header = QLabel("Notes for selected date")
        rn_header.setFont(self.header_font)
        right.addWidget(rn_header)

        self.date_notes_edit = QTextEdit()
        right.addWidget(self.date_notes_edit, stretch=1)

        btn_row = QHBoxLayout()
        save_date_note = QPushButton("Save Date Note")
        save_date_note.clicked.connect(self.save_date_note)
        btn_row.addWidget(save_date_note)

        del_date_note = QPushButton("Delete Date Note")
        del_date_note.clicked.connect(self.delete_date_note)
        btn_row.addWidget(del_date_note)

        right.addLayout(btn_row)
        layout.addLayout(right, 1)

        tab.setLayout(layout)
        return tab

    def on_calendar_date_clicked(self, qdate: QDate):
        key = qdate.toString("yyyy-MM-dd")
        txt = self.data.get("date_notes", {}).get(key, "")
        self.date_notes_edit.setPlainText(txt)

    def save_date_note(self):
        qdate = self.calendar.selectedDate()
        key = qdate.toString("yyyy-MM-dd")
        txt = self.date_notes_edit.toPlainText()
        self.data.setdefault("date_notes", {})[key] = txt
        save_data(self.data)
        QMessageBox.information(self, "Calendar", f"Saved note for {key}")

    def delete_date_note(self):
        qdate = self.calendar.selectedDate()
        key = qdate.toString("yyyy-MM-dd")
        if key in self.data.get("date_notes", {}):
            del self.data["date_notes"][key]
            self.date_notes_edit.clear()
            save_data(self.data)
            QMessageBox.information(self, "Calendar", f"Deleted note for {key}")
        else:
            QMessageBox.information(self, "Calendar", "No note to delete for selected date.")

    # ---------------------------
    # Theme & Utility
    # ---------------------------
    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.data.setdefault("settings", {})["dark_mode"] = self.dark_mode
        save_data(self.data)
        if self.dark_mode:
            self.apply_dark_theme()
            self.theme_btn.setText("🌙 Dark Mode")
        else:
            self.apply_light_theme()
            self.theme_btn.setText("☀ Light Mode")

    def apply_dark_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #0f1315; color: #e6eef0; font-family: "Segoe UI", sans-serif; }
            QTabWidget::pane { background: transparent; }
            QTabBar::tab { background: #131617; color: #cfe8e1; padding: 8px; border-radius: 6px; margin: 4px; }
            QTabBar::tab:selected { background: #1DB954; color: #07110a; font-weight: bold; }
            QPushButton { background-color: #1DB954; color: white; border-radius: 8px; padding: 6px 10px; }
            QPushButton:hover { background-color: #20e06a; }
            QLineEdit, QTextEdit, QListWidget, QSpinBox, QCalendarWidget { background-color: #141717; color: #e6eef0; border-radius: 6px; padding: 6px; }
            QListWidget::item { padding: 8px; }
        """)
        self.update_colors_after_theme()

    def apply_light_theme(self):
        self.setStyleSheet("""
            QWidget { background-color: #f6f8fb; color: #111111; font-family: "Segoe UI", sans-serif; }
            QTabWidget::pane { background: transparent; }
            QTabBar::tab { background: #e9eef3; color: #111111; padding: 8px; border-radius: 6px; margin: 4px; }
            QTabBar::tab:selected { background: #0078D7; color: #ffffff; font-weight: bold; }
            QPushButton { background-color: #0078D7; color: white; border-radius: 8px; padding: 6px 10px; }
            QPushButton:hover { background-color: #2894FF; }
            QLineEdit, QTextEdit, QListWidget, QSpinBox, QCalendarWidget { background-color: #ffffff; color: #111111; border-radius: 6px; padding: 6px; }
            QListWidget::item { padding: 8px; }
        """)
        self.update_colors_after_theme()

    def update_colors_after_theme(self):
        # update certain widget states (like task item colors) to match theme
        for i in range(self.task_list.count()):
            it = self.task_list.item(i)
            item = it.data(Qt.UserRole)
            if item.get("completed"):
                it.setForeground(Qt.gray)
            else:
                it.setForeground(Qt.black)

    def save_all(self):
        # flush UI content into data and save
        self.data["notes"] = self.global_notes.toPlainText()
        # tasks already mutated on actions; ensure they reflect list widget data
        tasks = []
        for i in range(self.task_list.count()):
            it = self.task_list.item(i)
            t = it.data(Qt.UserRole)
            tasks.append(t)
        self.data["tasks"] = tasks
        save_data(self.data)
        QMessageBox.information(self, "Saved", "All data saved to disk.")

    def show_about(self):
        QMessageBox.information(self, "About", f"Productivity Suite\n\nData stored in:\n{DATA_FILE}\n\nDesigned for a modern, centered workflow.")

# ---------------------------
# Run
# ---------------------------
def main():
    app = QApplication(sys.argv)
    window = ProductivityApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
