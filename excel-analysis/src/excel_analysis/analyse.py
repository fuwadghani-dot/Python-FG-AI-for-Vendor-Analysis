"""Analysis helpers"""
from __future__ import annotations
import pandas as pd
from typing import Iterable, Optional


def summary_stats(df: pd.DataFrame) -> pd.DataFrame:
    """Return descriptive statistics (transposed for readability)."""
    return df.describe(include="all").transpose()


def missing_summary(df: pd.DataFrame) -> pd.Series:
    """Return series of missing value counts sorted desc."""
    s = df.isna().sum()
    return s[s > 0].sort_values(ascending=False)


def column_types(df: pd.DataFrame) -> pd.Series:
    """Return inferred dtypes for columns."""
    return df.dtypes


def find_value_columns(df: pd.DataFrame) -> list[str]:
    """Return a list of numeric columns that look like 'value' or 'total'."""
    candidates = [c for c in df.select_dtypes(include=["number"]).columns if "value" in c.lower() or "total" in c.lower() or "net" in c.lower()]
    # fallback: any numeric columns
    if not candidates:
        candidates = list(df.select_dtypes(include=["number"]).columns)
    return candidates


def aggregate_by(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    agg: str = "sum",
    top_n: Optional[int] = 20,
    ascending: bool = False,
) -> pd.DataFrame:
    """Aggregate `value_col` grouped by `group_col` using aggregation `agg`.

    Returns a dataframe with columns [group_col, value_col] sorted by value.
    """
    if group_col not in df.columns:
        raise KeyError(f"group_col '{group_col}' not in DataFrame")
    if value_col not in df.columns:
        raise KeyError(f"value_col '{value_col}' not in DataFrame")

    if agg not in {"sum", "mean", "count", "median"}:
        raise ValueError("agg must be one of 'sum', 'mean', 'count', 'median'")

    grouped = df.groupby(group_col)[value_col]
    if agg == "sum":
        out = grouped.sum(min_count=1).reset_index()
    elif agg == "mean":
        out = grouped.mean().reset_index()
    elif agg == "count":
        out = grouped.count().reset_index()
    elif agg == "median":
        out = grouped.median().reset_index()

    out = out.rename(columns={value_col: "value"})
    out = out.sort_values(by="value", ascending=ascending)

    if top_n is not None:
        out = out.head(top_n)
    return out


def _find_column(df: pd.DataFrame, candidates: Iterable[str]) -> Optional[str]:
    """Return the actual column name in `df` that matches any of the `candidates` (case-insensitive), or None."""
    cols = list(df.columns)
    for cand in candidates:
        for c in cols:
            if str(c).strip().lower() == cand.strip().lower():
                return c
    return None


def build_vendor_report(
    df: pd.DataFrame,
    group_col: str,
    value_col: str,
    top_materials_per_plant: int = 10,
) -> dict:
    """Build report DataFrames for vendor analysis.

    Returns a mapping of sheet_name -> DataFrame to be written to the report.
    Sheets included:
      - supplier_totals
      - material_pivot (aggregates by Material)
      - plant_summary (per-plant totals/avg/count)
      - plant_top_materials (top N materials per Plant)

    This function is resilient to column name casing (it will detect 'material' or 'Material' etc.).
    """
    dfs = {}

    # supplier totals (full aggregation)
    dfs["supplier_totals"] = aggregate_by(df, group_col=group_col, value_col=value_col, agg="sum", top_n=None, ascending=False)

    # try to find Material and Plant columns case-insensitively
    material_col = _find_column(df, ["Material", "material"]) 
    plant_col = _find_column(df, ["Plant", "plant"]) 

    # material aggregates
    if material_col is not None:
        mat = (
            df.groupby(material_col).agg(
                total_value=(value_col, lambda s: s.sum(min_count=1)),
                avg_value=(value_col, "mean"),
                count_orders=(value_col, "count"),
            )
            .reset_index()
            .sort_values(by="total_value", ascending=False)
        )
        dfs["material_pivot"] = mat

    # plant summary
    if plant_col is not None:
        plant = (
            df.groupby(plant_col).agg(
                total_value=(value_col, lambda s: s.sum(min_count=1)),
                avg_value=(value_col, "mean"),
                count_orders=(value_col, "count"),
            )
            .reset_index()
            .sort_values(by="total_value", ascending=False)
        )
        dfs["plant_summary"] = plant

        # top materials per plant (only if material present)
        if material_col is not None:
            pm = (
                df.groupby([plant_col, material_col]).agg(total_value=(value_col, lambda s: s.sum(min_count=1))).reset_index()
            )
            # take top N materials per plant
            top_list = (
                pm.sort_values([plant_col, "total_value"], ascending=[True, False]).groupby(plant_col).head(top_materials_per_plant)
            )
            dfs["plant_top_materials"] = top_list

    return dfs
