from unittest.mock import Mock

from app.notifications import NotificationService, EmailNotifier, SMSNotifier


def test_notify_calls_all_observers():
    service = NotificationService()
    email, sms = Mock(), Mock()
    service.subscribe(email)
    service.subscribe(sms)
    service.notify(1, "hello")
    email.send.assert_called_once_with(1, "hello")
    sms.send.assert_called_once_with(1, "hello")


def test_notify_with_no_observers_is_safe():
    NotificationService().notify(1, "hello")


def test_email_notifier_stores_message(conn, patient):
    EmailNotifier(conn).send(patient, "Your appointment is confirmed")
    row = conn.execute("SELECT * FROM notifications WHERE user_id = ?",
                       (patient,)).fetchone()
    assert row["channel"] == "email"
    assert "confirmed" in row["message"]


def test_sms_notifier_stores_message(conn, patient):
    SMSNotifier(conn).send(patient, "Reminder")
    row = conn.execute("SELECT * FROM notifications WHERE user_id = ?",
                       (patient,)).fetchone()
    assert row["channel"] == "sms"
