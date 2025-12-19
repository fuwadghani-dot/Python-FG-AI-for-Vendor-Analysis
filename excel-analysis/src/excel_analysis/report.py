"""Report generation API (package-level implementation)."""
from __future__ import annotations
from pathlib import Path
from typing import Optional
from excel_analysis.io import save_excel_report, load_excel
from excel_analysis.clean import (
    strip_column_whitespace,
    standardize_columns,
    drop_high_missing_columns,
    parse_percent_column,
    coerce_numeric_columns,
)
from excel_analysis.analyse import find_value_columns, aggregate_by, build_vendor_report
from excel_analysis.viz import plot_supplier_totals


def generate(path: Path, out_dir: Optional[Path] = Path("reports/exports")) -> Path:
    """Generate a vendor report xlsx from the workbook at `path` and return the output path."""
    if not path.exists():
        raise FileNotFoundError(path)

    df = load_excel(path)
    # basic cleaning similar to Streamlit defaults
    df = strip_column_whitespace(df)
    df = standardize_columns(df)
    df = drop_high_missing_columns(df, threshold=1 - 0.1)

    # parse percent-like columns
    percent_like_cols = [c for c in df.columns if df[c].dtype == object and df[c].astype(str).str.contains('%').any()]
    for c in percent_like_cols:
        df = parse_percent_column(df, c, out_col=c, as_fraction=False)

    # coerce numeric-like
    df = coerce_numeric_columns(df)

    # choose grouping & value columns
    supplier_candidates = [c for c in df.columns if "supplier" in c.lower() or "vendor" in c.lower()]
    if not supplier_candidates:
        supplier_candidates = [c for c in df.columns if df[c].nunique() < 200 and df[c].dtype == object]
    if not supplier_candidates:
        raise RuntimeError("No supplier column detected")
    group_col = supplier_candidates[0]

    value_candidates = find_value_columns(df)
    if not value_candidates:
        raise RuntimeError("No value-like columns detected")
    val_col = value_candidates[0]

    # build report dataframes and figure
    dfs = build_vendor_report(df, group_col=group_col, value_col=val_col, top_materials_per_plant=10)
    # ensure supplier_totals exists
    if "supplier_totals" not in dfs:
        dfs["supplier_totals"] = aggregate_by(df, group_col=group_col, value_col=val_col, agg="sum", top_n=None)

    fig = plot_supplier_totals(dfs["supplier_totals"], group_col=group_col, value_col="value")

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "vendor_report.xlsx"
    b = save_excel_report(dfs, figures={"supplier_totals": fig})
    out_path.write_bytes(b)
    return out_path
