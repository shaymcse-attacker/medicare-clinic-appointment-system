class NotificationService:
    """Subject of the Observer pattern: booking code publishes events here
    without knowing which channels will deliver them."""

    def __init__(self):
        self._observers = []

    def subscribe(self, observer):
        self._observers.append(observer)

    def notify(self, user_id, message):
        for observer in self._observers:
            observer.send(user_id, message)


class _DbNotifier:
    channel = "generic"

    def __init__(self, conn):
        self.conn = conn

    def send(self, user_id, message):
        self.conn.execute(
            "INSERT INTO notifications (user_id, channel, message) VALUES (?, ?, ?)",
            (user_id, self.channel, message),
        )
        self.conn.commit()


class EmailNotifier(_DbNotifier):
    channel = "email"


class SMSNotifier(_DbNotifier):
    channel = "sms"
