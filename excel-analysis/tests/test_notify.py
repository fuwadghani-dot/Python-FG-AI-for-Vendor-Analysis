import pytest
from unittest.mock import patch, MagicMock
from excel_analysis.notify import send_email
from pathlib import Path


def test_send_email_calls_smtp(monkeypatch):
    # patch smtplib.SMTP and SMTP_SSL
    mock_smtp = MagicMock()
    with patch("smtplib.SMTP", return_value=mock_smtp):
        send_email("subj", "body", "smtp.example.com", 587, "from@example.com", "to@example.com", smtp_user=None, smtp_pass=None, attachments=None)
        assert mock_smtp.__enter__().starttls.called
        assert mock_smtp.__enter__().send_message.called

    mock_ssl = MagicMock()
    with patch("smtplib.SMTP_SSL", return_value=mock_ssl):
        send_email("subj", "body", "smtp.example.com", 465, "from@example.com", "to@example.com")
        assert mock_ssl.__enter__().send_message.called


def test_send_email_with_attachment(tmp_path, monkeypatch):
    f = tmp_path / "a.txt"
    f.write_text("hello")
    mock_smtp = MagicMock()
    with patch("smtplib.SMTP", return_value=mock_smtp):
        send_email("subj", "body", "smtp.example.com", 587, "from@example.com", "to@example.com", attachments=[f])
        assert mock_smtp.__enter__().send_message.called
