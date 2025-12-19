"""Cleaning helpers"""
from __future__ import annotations
import re
from typing import Iterable
import pandas as pd


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: strip, lower, replace spaces with underscores."""
    df = df.copy()
    df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]
    return df


def strip_column_whitespace(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from string columns and column names."""
    df = df.copy()
    # fix column names that have trailing spaces (e.g., 'Total Value ')
    df.columns = [str(c).strip() for c in df.columns]
    # strip string values
    obj_cols = df.select_dtypes(include=["object"]).columns
    for c in obj_cols:
        df[c] = df[c].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def drop_high_missing_columns(df: pd.DataFrame, threshold: float = 0.9) -> pd.DataFrame:
    """Drop columns with a fraction of non-missing values below (1-threshold).

    threshold: fraction of values required to be non-missing (0-1)
    """
    min_non_na = int(len(df) * threshold)
    return df.dropna(axis=1, thresh=min_non_na)


def parse_date_columns(df: pd.DataFrame, candidates: list[str]) -> pd.DataFrame:
    """Try parsing candidate date columns to datetime."""
    df = df.copy()
    for c in candidates:
        if c in df.columns:
            try:
                df[c] = pd.to_datetime(df[c], errors="coerce")
            except Exception:
                pass
    return df


from typing import Optional

def _extract_percent(s: str) -> Optional[float]:
    """Extract a numeric percent value from a string like '-3.2%' or '3.2%'"""
    if not isinstance(s, str):
        return None
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*%", s)
    if m:
        try:
            return float(m.group(1))
        except Exception:
            return None
    # sometimes value is like '-3.2' without % sign
    m2 = re.search(r"(-?\d+(?:\.\d+)?)", s)
    if m2:
        try:
            return float(m2.group(1))
        except Exception:
            return None
    return None


def parse_percent_column(df: pd.DataFrame, col: str, out_col: Optional[str] = None, as_fraction: bool = False) -> pd.DataFrame:
    """Parse a column containing percentage strings into numeric values.

    Args:
        df: input dataframe
        col: column to parse (must exist)
        out_col: if provided, write results to new column name; otherwise overwrite
        as_fraction: return fractions (0.032) instead of percent (3.2)
    """
    df = df.copy()
    if col not in df.columns:
        return df
    target = out_col or col
    df[target] = pd.to_numeric(df[col].apply(lambda x: _extract_percent(x) if pd.notna(x) else None), errors="coerce")
    if as_fraction:
        df[target] = df[target].apply(lambda x: x / 100.0 if pd.notna(x) else x)
    return df


def parse_conditions_column(df: pd.DataFrame, col: str, prefix: str = "cond_") -> pd.DataFrame:
    """Parse a composite 'Conditions Not Applied Percentage' column like
    'YDRG - -3.2%, YSTD - -2.0%' into separate numeric columns.

    For each found code (e.g., YDRG) we create a column `prefix + code` with the
    numeric percent (as percent, not fraction).
    """
    df = df.copy()
    if col not in df.columns:
        return df

    def parse_row(s: str):
        res = {}
        if not isinstance(s, str):
            return res
        parts = [p.strip() for p in s.split(",") if p.strip()]
        for p in parts:
            # robust parse: split on first '-' to separate code from value part
            if "-" in p:
                left, right = p.split("-", 1)
                code = left.strip().replace(" ", "_")
                # extract numeric value anywhere in the right side
                m = re.search(r"(-?\d+(?:\.\d+)?)", right)
                if m:
                    try:
                        val = float(m.group(1))
                    except Exception:
                        val = None
                    res[code] = val
        return res

    # gather all codes present in the sheet (scan a sample)
    codes = set()
    for v in df[col].dropna().astype(str).head(500):
        codes.update(parse_row(v).keys())
    for code in sorted(codes):
        df[f"{prefix}{code}"] = df[col].apply(lambda s: parse_row(s).get(code) if pd.notna(s) else None)
    return df


from typing import Iterable, Optional

def coerce_numeric_columns(df: pd.DataFrame, candidates: Optional[Iterable[str]] = None) -> pd.DataFrame:
    """Coerce object columns that look numeric into numeric dtype.

    If `candidates` is provided, only attempt those columns; otherwise all object cols.
    """
    df = df.copy()
    cols = list(candidates) if candidates is not None else list(df.select_dtypes(include=["object"]).columns)
    for c in cols:
        # try converting; ignore columns that would become all-NaN
        coerced = pd.to_numeric(df[c].astype(str).str.replace('%', '').str.replace(',', '').str.strip(), errors='coerce')
        if coerced.notna().sum() >= max(1, len(df) * 0.5):  # require at least some values
            df[c] = coerced
    return df
