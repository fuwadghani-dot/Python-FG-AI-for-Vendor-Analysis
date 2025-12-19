import pandas as pd
from excel_analysis.viz import plot_supplier_totals


def test_plot_supplier_totals_basic():
    agg = pd.DataFrame({"Supplier": ["A", "B"], "value": [300, 125]})
    fig = plot_supplier_totals(agg, group_col="Supplier", value_col="value")
    # basic checks
    assert hasattr(fig, "data")
    assert len(fig.data) >= 1
    # ensure x values present
    xs = list(fig.data[0].x)
    assert set(xs) == {"A", "B"}
