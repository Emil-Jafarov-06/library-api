OUTBOX_PATH = "outbox.txt"


class Notifier:
    def send(self, email, subject, body):
        raise NotImplementedError


class MockEmailNotifier(Notifier):
    def __init__(self, outbox_path=OUTBOX_PATH):
        self.outbox_path = outbox_path
        self.sent = []

    def send(self, email, subject, body):
        self.sent.append({"to": email, "subject": subject, "body": body})
        with open(self.outbox_path, "a") as f:
            f.write("TO: " + email + " | SUBJECT: " + subject + " | BODY: " + body + "\n")


notifier = MockEmailNotifier()


def send_email(email, subject, body):
    notifier.send(email, subject, body)
