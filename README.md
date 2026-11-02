# ReConnect – Smart Campus Lost & Found System

## Requirements
- Python 3.9 or newer
- VS Code (recommended)
- Internet connection for the first installation of Streamlit and pandas

## Setup
Open this folder in VS Code, then open the terminal and run:

```bash
python -m pip install -r requirements.txt
python -m streamlit run main.py
```

If `python` does not work on Windows, try `py` instead:

```bash
py -m pip install -r requirements.txt
py -m streamlit run main.py
```

The app opens in your browser, usually at `http://localhost:8501`.

## Features
- Dashboard and report statistics
- Submit lost-item reports
- Submit found-item reports
- Search by keyword, report type, category, and status
- View records and update status (Open, Claimed, Returned)
- SQLite database created automatically as `reconnect.db`

## Demo steps
1. Add a Lost report for an item such as an ID card.
2. Add a Found report for an item such as a water bottle.
3. Open Search Items and search for a keyword.
4. Open Manage Records and update a record to Claimed or Returned.

## Important
This is a local academic prototype. Contact details are not shown in public search results. Use ownership verification before returning an item.
