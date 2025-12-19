import pandas as pd
from excel_analysis.io import load_excel, to_excel_bytes


def test_load_and_save(tmp_path):
    df = pd.DataFrame({"a": [1, 2, None], "b": ["x", "y", "z"]})
    p = tmp_path / "sample.xlsx"
    df.to_excel(p, index=False)

    df2 = load_excel(p)
    assert list(df2.columns) == ["a", "b"]

    b = to_excel_bytes(df2)
    assert isinstance(b, (bytes, bytearray))
