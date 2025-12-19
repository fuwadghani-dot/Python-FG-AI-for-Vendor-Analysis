"""Configuration helpers reading environment variables."""
from __future__ import annotations
import os
from typing import Optional

SERVICE_TOKEN: Optional[str] = os.getenv("SERVICE_TOKEN")

# SMTP settings for alerts
SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST")
SMTP_PORT: Optional[int] = int(os.getenv("SMTP_PORT", "0")) if os.getenv("SMTP_PORT") else None
SMTP_USER: Optional[str] = os.getenv("SMTP_USER")
SMTP_PASS: Optional[str] = os.getenv("SMTP_PASS")
ALERT_FROM: Optional[str] = os.getenv("ALERT_FROM")
ALERT_TO: Optional[str] = os.getenv("ALERT_TO")
SEND_ATTACHMENTS: bool = os.getenv("SEND_ATTACHMENTS", "false").lower() in ("1", "true", "yes")
REPORT_BASE_URL: Optional[str] = os.getenv("REPORT_BASE_URL")


def alerting_enabled() -> bool:
    return bool(SMTP_HOST and ALERT_TO and ALERT_FROM)
