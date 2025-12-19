inspect_workbook.py

Usage:

1. Activate your virtualenv (from project root):

```bash
source .venv/bin/activate
```

2. Install dependencies (if not already installed):

```bash
pip install -r requirements.txt
```

3. Run the inspector:

```bash
python scripts/inspect_workbook.py "../Data AI for Vendor analysis.xlsx"
```

This prints a summary for each sheet and writes small sample CSVs to `reports/inspections/` for review.
