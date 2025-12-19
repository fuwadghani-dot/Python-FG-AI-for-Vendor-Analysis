import pandas as pd
from excel_analysis.analyse import build_vendor_report


def test_build_vendor_report_case_insensitive_columns():
    df = pd.DataFrame({
        "supplier": ["A", "B", "A"],
        "material": ["M1", "M2", "M1"],
        "plant": ["P1", "P1", "P2"],
        "value": [100, 200, 50],
    })
    extra = build_vendor_report(df, group_col="supplier", value_col="value", top_materials_per_plant=2)
    assert "material_pivot" in extra
    assert "plant_summary" in extra
    assert "plant_top_materials" in extra
