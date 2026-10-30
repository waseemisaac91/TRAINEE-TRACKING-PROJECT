# TRAINEE-TRACKING-PROJECT
TRAINEE TRACKING PROJECT By Waseem &amp; Dana
# Database Module – Google Drive → PostgreSQL Importer

Desktop app (PyQt6) that imports data from Google Sheets (Google Drive) into a PostgreSQL database and lets you browse and query the result.

## Run

```
python main.py
```

A login/settings dialog opens first (database connection details). After you accept, the main window opens.

## What it does

| Tab | Purpose |
|---|---|
| **Check** | Compares the headers of the Google Sheets with the PostgreSQL columns and reports what matches. |
| **Import** | Previews and imports each table, or all at once, in dependency order. |
| **Tables** | Browse any table (trainees, applications, mentors, users, projecttracking). |
| **Custom Query** | Run any SQL (SELECT / INSERT / UPDATE / DELETE) and see the results. |

### Import mapping

| Sheet | Imported into |
|---|---|
| Applications | `trainees`, `applications` |
| Mentor | `mentors` |
| Users | `users` (passwords are hashed) |
| Interviews | `projecttracking` |

Tables are created automatically if they do not exist. Duplicate rows are skipped, and an "update" mode can refresh existing rows.

### Table view features

- Column widths adapt to the content; horizontal and vertical scrolling
- Record view: double-click a row to see all fields of a record, with Previous / Next and Copy
- Filter box (all columns), click a header to sort, rows-per-page selector
- Ctrl+C copies the selected rows

## Files

| File | Description |
|---|---|
| `main.py` | Main application: importers, UI tabs, stylesheet |
| `paged_table.py` | Table widget with record view, filter, sort and paging |
| `Ui.py` | Settings/login dialog and config helpers |
| `database_service.py` | Password hashing helper (`hash_password`) |
| `google_drive_service.py` | Google Drive / Sheets access (in `services/` or next to `main.py`) |

## Requirements

- Python 3.10+
- PostgreSQL server you can connect to
- Google service credentials configured for `google_drive_service`

```
pip install PyQt6 psycopg2-binary gspread google-auth
```

(Install whatever extra packages your `google_drive_service.py` and `database_service.py` import.)
