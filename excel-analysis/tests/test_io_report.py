import pandas as pd
from excel_analysis.io import save_excel_report
import io


def test_save_excel_report_basic():
    df1 = pd.DataFrame({"Supplier": ["A", "B"], "value": [100, 200]})
    df2 = pd.DataFrame({"col": [1, 2, 3]})
    # No figures provided
    b = save_excel_report({"sheet1": df1, "sheet2": df2}, figures=None)
    assert isinstance(b, (bytes, bytearray))
    # ensure we can read the sheets back
    xls = pd.ExcelFile(io.BytesIO(b))
    assert set(xls.sheet_names) >= {"sheet1", "sheet2"}
