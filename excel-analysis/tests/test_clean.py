import pandas as pd
from excel_analysis.clean import parse_percent_column, parse_conditions_column, strip_column_whitespace, coerce_numeric_columns


def test_parse_percent_column():
    df = pd.DataFrame({"pct_str": ["-3.2%", "2.5%", None, "5"]})
    out = parse_percent_column(df, "pct_str", out_col="pct", as_fraction=False)
    assert out["pct"].iloc[0] == -3.2
    assert out["pct"].iloc[1] == 2.5
    assert pd.isna(out["pct"].iloc[2])
    out2 = parse_percent_column(df, "pct_str", out_col="pctf", as_fraction=True)
    assert abs(out2["pctf"].iloc[0] + 0.032) < 1e-9


def test_parse_conditions_column():
    df = pd.DataFrame({"conditions": ["YDRG - -3.2%, YSTD - -2.0%", None, "YDRG - 1.5%"]})
    out = parse_conditions_column(df, "conditions", prefix="cond_")
    assert "cond_YDRG" in out.columns
    assert out["cond_YDRG"].iloc[0] == -3.2
    assert out["cond_YDRG"].iloc[2] == 1.5
    assert pd.isna(out["cond_YSTD"].iloc[2])


def test_strip_and_coerce():
    df = pd.DataFrame({"A ": ["  x  ", "y"], "num": ["1", "2"]})
    out = strip_column_whitespace(df)
    assert "A" in out.columns
    assert out["A"].iloc[0] == "x"
    out2 = coerce_numeric_columns(out, candidates=["num"]) 
    assert out2["num"].dtype.name.startswith("int") or out2["num"].dtype.name.startswith("float")
