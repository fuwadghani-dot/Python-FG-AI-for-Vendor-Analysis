"""Recurring report runner and CLI helpers."""
from __future__ import annotations
from pathlib import Path
import json
import logging
from datetime import datetime
from typing import Optional

from excel_analysis.report import generate
from excel_analysis import config
from excel_analysis.notify import send_email

logger = logging.getLogger(__name__)

STATUS_PATH = Path("reports/status.json")


class ReportRunner:
    """Run and track reports produced from Excel files.

    Usage:
        runner = ReportRunner()
        runner.run_once("/path/to/workbook.xlsx")
    """

    def __init__(self, output_dir: Optional[Path] = None) -> None:
        self.output_dir = Path(output_dir) if output_dir else Path("reports/exports")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _write_status(self, status: dict) -> None:
        STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with STATUS_PATH.open("w", encoding="utf-8") as fh:
            json.dump(status, fh, indent=2, default=str)

    def run_once(self, workbook_path: str) -> Path:
        path = Path(workbook_path)
        start = datetime.utcnow().isoformat()
        status = {"last_start": start, "workbook": str(path), "status": "running"}
        self._write_status(status)
        logger.info("Running report for %s", path)
        try:
            out = generate(path, out_dir=self.output_dir)
            status.update({"last_success": datetime.utcnow().isoformat(), "status": "success", "report_path": str(out)})
            logger.info("Report written to %s", out)

            # send success alert if configured
            try:
                if config.alerting_enabled():
                    subject = f"Vendor report succeeded: {path.name}"
                    link = None
                    if config.REPORT_BASE_URL:
                        link = f"{config.REPORT_BASE_URL.rstrip('/')}/{Path(status['report_path']).name}"
                    body = f"Report succeeded for workbook: {path}\nReport: {status['report_path']}"
                    if link:
                        body += f"\nPublic link: {link}"
                    if config.SEND_ATTACHMENTS:
                        send_email(subject, body, config.SMTP_HOST, config.SMTP_PORT, config.ALERT_FROM, config.ALERT_TO, config.SMTP_USER, config.SMTP_PASS, attachments=[Path(status['report_path'])])
                    else:
                        send_email(subject, body, config.SMTP_HOST, config.SMTP_PORT, config.ALERT_FROM, config.ALERT_TO, config.SMTP_USER, config.SMTP_PASS)
            except Exception:
                logger.exception("Failed to send success alert")

        except Exception as exc:  # pragma: no cover - integration error handling
            logger.exception("Report generation failed: %s", exc)
            status.update({"status": "failed", "error": str(exc)})
            # send failure alert
            try:
                if config.alerting_enabled():
                    subject = f"Vendor report failed: {path.name}"
                    body = f"Report failed for workbook: {path}\nError: {exc}"
                    send_email(subject, body, config.SMTP_HOST, config.SMTP_PORT, config.ALERT_FROM, config.ALERT_TO, config.SMTP_USER, config.SMTP_PASS)
            except Exception:
                logger.exception("Failed to send failure alert")
            raise
        finally:
            status.update({"last_end": datetime.utcnow().isoformat()})
            self._write_status(status)
        return out


def read_status() -> dict:
    if not STATUS_PATH.exists():
        return {}
    return json.loads(STATUS_PATH.read_text(encoding="utf-8"))
