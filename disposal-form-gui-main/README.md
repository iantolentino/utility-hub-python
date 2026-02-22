# Disposal Form GUI

Simple single-file Python GUI to record disposal sessions (White paper, Colored Paper, Plastic, Garbage) and append them to an Excel workbook.

---

## Features

* Minimal, modern Tkinter + `ttk` UI.
* Centers the window on screen.
* Four fixed categories: **White paper**, **Colored Paper**, **Plastic**, **Garbage**.
* Quantity units: **KG** or **Grams**.
* Live total (displayed in KG).
* "Save Session" appends a grouped block to an Excel workbook including a timestamp, category rows, and a total in KG.
* The UI shows the full path to the Excel file so you can easily open or verify it.
* Small visual spacing is added after each session block in the spreadsheet.

---

## Requirements

* Python 3.8+ (should work with 3.7 in most cases)
* `openpyxl` for Excel read/write

Install dependencies with pip:

```bash
pip install openpyxl
```

---

## Files

* `disposal_form.py` — the single-file program (the GUI app).
* `disposal_log.xlsx` — default target Excel file (created automatically when you save a session).

> **Default Excel path**: The program will attempt to save to `Documents/disposal_log.xlsx` in the current user's home folder. If the `Documents` folder does not exist, it uses the home directory (e.g. `C:\Users\<you>\disposal_log.xlsx`). You can change this path in the source by editing the `EXCEL_FILENAME` variable.

---

## How the Excel output is organized

Each saved session appends a small block to the active worksheet with this structure:

```
Date/Time Added: 2025-10-13 14:12:05  <-- bold timestamp row
Category | Quantity | Unit                     <-- bold header row
White paper   | 0.2  | KG
Colored Paper | 2.5  | KG
Plastic       | 1.0  | KG
Garbage       | 0.2  | KG
Total:        | 3.900| KG                     <-- bold total row

(then one blank row inserted for spacing)
```

The code writes numeric quantities when the input can be parsed as a float; otherwise it writes the original text. The total is always stored as a numeric value (rounded to 3 decimals) in KG.

---

## Run the app

```bash
python disposal_form.py
```

* Enter quantities for each category and choose the unit (KG or Grams).
* Click **Save Session (Add new data)** to append the block to the Excel file. The UI will display the exact Excel path and a status message showing the saved total.
* Use **Open Excel File** to open the target workbook (OS default program will be used).

---

## Customization

* **Change categories**: edit the `CATEGORIES` list near the top of the file.
* **Change units list**: edit `UNIT_OPTIONS`.
* **Change Excel filename/location**: modify the `EXCEL_FILENAME` variable. Example:

```python
EXCEL_FILENAME = r"C:\path\to\my\folder\my_disposal_log.xlsx"
```

* **Adjust spacing**: the program adds a merged blank row below each session and sets its `row_dimensions.height`. Tweak the value `ws.row_dimensions[next_row].height = 12` inside `append_session_to_excel()` to make the gap smaller or larger.

---

## Troubleshooting

* **PermissionError / Save failed**: If Excel (or another program) has `disposal_log.xlsx` open, Python cannot overwrite the file. Close the file in Excel and try saving again. Alternatively, change `EXCEL_FILENAME` to a different path before saving.

* **Quantities not summing / invalid input**: Only numeric input will be parsed as numbers. Non-numeric text will be written literally into the Quantity cell and treated as `0.0` for the total calculation. Use numbers (e.g. `0.2`, `250` for grams) to get correct totals.

* **Excel formatting / line wrapping**: If you want the Excel cells to wrap text or look nicer, open the workbook in Excel and apply formatting (wrap text, column widths, fonts) as desired. The program writes basic values and bolds headers/totals.

---

## Suggested improvements (ideas)

* Add a fallback save behavior that writes to a timestamped alternate file when the primary file is locked (prevent data loss). This was included in an earlier patch and can be re-enabled if you want automatic conflict handling.
* Add a CSV export option.
* Add per-session notes or a free-text field.
* Allow optional categories or dynamically adding categories from the UI.
* Add user preferences (default save path, auto-open after save).

---

## License

Use this project freely for personal or commercial use. No warranty provided — use at your own risk.

Tell me which one you want next.
