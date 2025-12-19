import tempfile
from pathlib import Path
from excel_analysis.runner import ReportRunner, read_status


def test_run_once_creates_report(tmp_path):
    # use the sample source workbook
    src = Path(__file__).parents[1] / "../Data AI for Vendor analysis.xlsx"
    src = src.resolve()
    assert src.exists()

    runner = ReportRunner(output_dir=tmp_path / "exports")
    out = runner.run_once(str(src))
    assert Path(out).exists()
    status = read_status()
    assert status.get("status") == "success"
    assert status.get("report_path") == str(out)
