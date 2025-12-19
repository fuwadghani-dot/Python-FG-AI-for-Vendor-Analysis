"""Simple email notifier using smtplib."""
from __future__ import annotations
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable, Optional


def send_email(
    subject: str,
    body: str,
    smtp_host: str,
    smtp_port: int | None,
    from_addr: str,
    to_addrs: str | Iterable[str],
    smtp_user: Optional[str] = None,
    smtp_pass: Optional[str] = None,
    attachments: Optional[Iterable[Path]] = None,
) -> None:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = from_addr
    msg["To"] = ",".join(to_addrs) if isinstance(to_addrs, (list, tuple)) else to_addrs
    msg.set_content(body)

    # attach files if any
    if attachments:
        for p in attachments:
            try:
                b = p.read_bytes()
                maintype = "application"
                subtype = "octet-stream"
                msg.add_attachment(b, maintype=maintype, subtype=subtype, filename=p.name)
            except Exception:
                # ignore attachment errors
                continue

    port = smtp_port or 0
    if port == 465:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, port, context=context) as server:
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, port or 587) as server:
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.send_message(msg)
