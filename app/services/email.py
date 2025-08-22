class EmailService:
    """Stub email service. Replace with SendGrid/SES/etc."""

    def send_verification(self, to: str, token: str) -> None:
        # TODO: integrate provider
        print(f"[EMAIL] Verify {to}: token={token}")

    def send_password_reset(self, to: str, token: str) -> None:
        # TODO: integrate provider
        print(f"[EMAIL] Reset {to}: token={token}")


def get_email_service() -> EmailService:
    return EmailService()
