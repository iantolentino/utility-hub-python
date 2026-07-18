# 📂 File Organizer Script

A professional, extensible **file organization tool** built with Python.  
It automatically sorts files into categorized subfolders (e.g., Images, Documents, Videos) based on their extensions, with optional **real-time monitoring** (`--watch` mode).  

This project demonstrates **clean architecture, modern Python practices, and contributor-friendly design**, making it practical for everyday use and a strong portfolio addition.

---

## ✨ Features

- **Clean Architecture** – built around a `FileOrganizer` class for separation of concerns.  
- **Extensible Categories** – update a single `FILE_CATEGORIES` dictionary to support new file types.  
- **Robust Handling** – duplicate filenames are renamed safely (e.g., `file(1).txt`).  
- **Logging System** – operations and errors are tracked in `file_organizer.log`.  
- **Modern Practices** – `pathlib`, `argparse`, `logging`, and type hints.  
- **Optional Watch Mode** – automatically organizes files as soon as they appear (via `watchdog`).  
- **Cross-Platform** – works on Windows, Linux, and macOS.

---

## 🛠️ Tech Stack

- **Python 3.8+**  
- `pathlib`, `shutil`, `argparse`, `logging` (standard library)  
- `watchdog` (for `--watch` mode)

---

## 📦 Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/file-organizer.git
   cd file-organizer
  

2. (Optional) Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate   # Linux/Mac
   venv\Scripts\activate      # Windows
   ```

3. Install dependencies:

   ```bash
   pip install watchdog
   ```

---

## 🚀 Usage

### Basic Organization

Organize all files in a directory into subfolders:

```bash
python file_organizer.py /path/to/your/directory
```

### Watch Mode

Continuously monitor a directory and auto-organize new files:

```bash
python file_organizer.py /path/to/your/directory --watch
```

### Example

Before:

```
Downloads/
 ├── photo.jpg
 ├── report.pdf
 ├── movie.mp4
```

After:

```
Downloads/
 ├── Images/
 │    └── photo.jpg
 ├── Documents/
 │    └── report.pdf
 ├── Videos/
 │    └── movie.mp4
```

---

## 📂 Project Structure

```
file_organizer.py   # Main script
file_organizer.log  # Log file (auto-generated)
```

---

## 🤝 Contributing

Contributions are welcome!

* Follow **PEP 8** coding style.
* Use type hints and docstrings for clarity.
* Submit issues or pull requests for new features or categories.

---

## 📝 License

MIT License © 2025 \[Ian Tolentino]

---

## 💡 Future Improvements

* Config file support (e.g., JSON/YAML for categories).
* Recursive subdirectory organization.
* Unit tests with `pytest`.
* GUI/desktop integration for non-CLI users.
