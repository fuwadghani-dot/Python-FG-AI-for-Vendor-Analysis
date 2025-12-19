"""Inspect an Excel workbook and print per-sheet summaries.

Usage:
    python scripts/inspect_workbook.py "../Data AI for Vendor analysis.xlsx"

This script requires pandas and openpyxl to be installed in the active Python environment.
It prints sheet names, shapes, sample columns, missing-value counts, dtypes summary, and 3 sample rows.
It also writes per-sheet sample CSVs into `reports/inspections/` for quick review.
"""
from __future__ import annotations
import sys
from pathlib import Path

try:
    import pandas as pd
except Exception as e:
    print("ERROR: pandas is not installed in the current environment.\n\n", e)
    print("Install dependencies with: python -m pip install -r requirements.txt")
    sys.exit(2)


def inspect(path: Path, max_cols: int = 12, sample_rows: int = 3):
    if not path.exists():
        print(f"File not found: {path}")
        return

    xls = pd.ExcelFile(path, engine="openpyxl")
    outdir = Path("reports/inspections")
    outdir.mkdir(parents=True, exist_ok=True)

    print(f"Workbook: {path}  |  sheets: {len(xls.sheet_names)}")
    for s in xls.sheet_names:
        print('\n' + '=' * 80)
        print(f"Sheet: {s}")
        df = pd.read_excel(xls, sheet_name=s, engine="openpyxl")
        print("shape:", df.shape)

        cols = list(df.columns)
        print("columns (first {}): {}".format(max_cols, cols[:max_cols]))

        # dtype summary
        dtypes = df.dtypes.apply(lambda x: x.name).value_counts().to_dict()
        print("dtypes:", dtypes)

        # missing values
        miss = df.isna().sum().sort_values(ascending=False)
        print("top missing:", dict(miss.head(10)))

        # unique value counts for small-cardinality columns
        uniq = {c: int(df[c].nunique(dropna=True)) for c in cols[:max_cols]}
        print("uniques (first {} cols): {}".format(max_cols, uniq))

        # numeric summary
        num = df.select_dtypes(include=["number"]).shape[1]
        print("numeric columns:", num)

        # sample rows
        print("sample rows:")
        print(df.head(sample_rows).to_dict(orient='records'))

        # write a small sample csv for review
        outpath = outdir / f"{s.replace(' ', '_')}_sample.csv"
        df.head(100).to_csv(outpath, index=False)
        print(f"Wrote sample CSV to: {outpath}")


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/inspect_workbook.py PATH_TO_XLSX")
        sys.exit(1)
    inspect(Path(sys.argv[1]))
