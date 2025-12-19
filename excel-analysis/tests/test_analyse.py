import pandas as pd
from excel_analysis.analyse import aggregate_by, find_value_columns


def test_aggregate_by_sum_and_sort():
    df = pd.DataFrame({
        "Supplier": ["A", "A", "B", "C", "B"],
        "Total": [100, 200, 50, 25, 75],
    })
    agg = aggregate_by(df, group_col="Supplier", value_col="Total", agg="sum", top_n=None, ascending=False)
    assert list(agg["Supplier"]) == ["A", "B", "C"]
    assert list(agg["value"]) == [300, 125, 25]


def test_find_value_columns_prefers_value():
    df = pd.DataFrame({"a": [1, 2], "total_val": [10, 20], "net_value": [5, 6]})
    vals = find_value_columns(df)
    assert "total_val" in vals or "net_value" in vals
