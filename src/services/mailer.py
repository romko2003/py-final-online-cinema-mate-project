from dataclasses import dataclass


@dataclass(frozen=True)
class OutgoingEmail:
    to: str
    subject: str
    body: str


class MailerInterface:
    def send(self, email: OutgoingEmail) -> None:
        raise NotImplementedError


class DevConsoleMailer(MailerInterface):
    def send(self, email: OutgoingEmail) -> None:
        # На техчеку достатньо stub-а (реальний SMTP не обов'язковий)
        print(f"[MAIL] to={email.to} subject={email.subject}\n{email.body}\n")
