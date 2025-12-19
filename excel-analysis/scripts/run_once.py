"""CLI: run report once on provided Excel file."""
from __future__ import annotations
import argparse
from pathlib import Path
from excel_analysis.runner import ReportRunner


def main():
    p = argparse.ArgumentParser(description="Run vendor report once on an Excel workbook")
    p.add_argument("workbook", help="Path to the Excel workbook")
    p.add_argument("--outdir", help="Optional output dir for reports", default="reports/exports")
    args = p.parse_args()

    runner = ReportRunner(output_dir=Path(args.outdir))
    out = runner.run_once(args.workbook)
    print(f"Report written to: {out}")


if __name__ == '__main__':
    main()
