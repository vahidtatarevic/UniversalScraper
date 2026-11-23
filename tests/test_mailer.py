from typing import ClassVar

from app import mailer


class FakeSMTP:
    """Stands in for smtplib.SMTP and records what would go over the wire."""

    instances: ClassVar[list["FakeSMTP"]] = []

    def __init__(self, host, port):
        self.host, self.port = host, port
        self.started_tls = False
        self.logged_in_as = None
        self.sent = []
        FakeSMTP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        self.started_tls = True

    def login(self, user, password):
        self.logged_in_as = (user, password)

    def send_message(self, message):
        self.sent.append(message)


def configure_smtp(monkeypatch):
    FakeSMTP.instances = []
    monkeypatch.setattr(mailer.smtplib, "SMTP", FakeSMTP)
    monkeypatch.setattr(mailer, "SMTP_HOST", "smtp.example.com")
    monkeypatch.setattr(mailer, "SMTP_PORT", 587)
    monkeypatch.setattr(mailer, "SMTP_USER", "sender@example.com")
    monkeypatch.setattr(mailer, "SMTP_PASSWORD", "app-password")
    monkeypatch.setattr(mailer, "MAIL_FROM", None)
    monkeypatch.setattr(mailer, "BASE_URL", "https://scraper.example.com")


def test_sends_verification_link_over_smtp(monkeypatch):
    configure_smtp(monkeypatch)
    mailer.send_verification_email("user@example.com", "abc123")

    smtp = FakeSMTP.instances[0]
    assert (smtp.host, smtp.port) == ("smtp.example.com", 587)
    assert smtp.started_tls
    assert smtp.logged_in_as == ("sender@example.com", "app-password")
    message = smtp.sent[0]
    assert message["To"] == "user@example.com"
    assert message["From"] == "sender@example.com"
    assert "https://scraper.example.com/verify?token=abc123" in message.get_content()


def test_sends_from_mail_from_address_when_set(monkeypatch):
    # Providers like Resend use a username such as "resend", not an address.
    configure_smtp(monkeypatch)
    monkeypatch.setattr(mailer, "SMTP_USER", "resend")
    monkeypatch.setattr(mailer, "MAIL_FROM", "Scraper <noreply@scraper.example.com>")
    mailer.send_verification_email("user@example.com", "abc123")

    message = FakeSMTP.instances[0].sent[0]
    assert message["From"] == "Scraper <noreply@scraper.example.com>"
    assert FakeSMTP.instances[0].logged_in_as == ("resend", "app-password")


def test_prints_link_when_smtp_is_not_configured(monkeypatch, capsys):
    configure_smtp(monkeypatch)
    monkeypatch.setattr(mailer, "SMTP_USER", None)
    mailer.send_verification_email("user@example.com", "abc123")

    assert FakeSMTP.instances == []
    assert "https://scraper.example.com/verify?token=abc123" in capsys.readouterr().out
